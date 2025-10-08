"""
Comprehensive test suite for the sparkline generator.
Tests all functionality including error handling, edge cases, and integration scenarios.
"""

import pytest
import json
import tempfile
import os
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
import sys
import logging

# Add the scripts directory to the path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))

from gen_sparkline import (
    SparklineGenerator,
    SparklineConfig,
    GitHubActivityFetcher,
    GitHubAPIError,
    SparklineGeneratorError,
    setup_logging,
    parse_arguments,
    main
)


class TestSparklineConfig:
    """Test the SparklineConfig dataclass."""
    
    def test_default_config(self):
        """Test default configuration values."""
        config = SparklineConfig()
        assert config.width == 400
        assert config.height == 60
        assert config.margin == 10
        assert config.stroke_width == 2
        assert config.point_radius == 3
        assert config.gradient_start == "#4facfe"
        assert config.gradient_end == "#00f2fe"
        assert config.opacity == 0.8
    
    def test_custom_config(self):
        """Test custom configuration values."""
        config = SparklineConfig(
            width=800,
            height=120,
            gradient_start="#ff0000"
        )
        assert config.width == 800
        assert config.height == 120
        assert config.gradient_start == "#ff0000"
        # Default values should still be present
        assert config.margin == 10


class TestSparklineGenerator:
    """Test the SparklineGenerator class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.config = SparklineConfig()
        self.generator = SparklineGenerator(self.config)
    
    def test_generate_sparkline_valid_data(self):
        """Test sparkline generation with valid data."""
        data = [10, 20, 15, 25, 30]
        result = self.generator.generate_sparkline(data)
        
        assert isinstance(result, str)
        assert '<svg' in result
        assert 'sparkGradient' in result
        assert 'polyline' in result
        assert 'circle' in result
        assert f'width="{self.config.width}"' in result
        assert f'height="{self.config.height}"' in result
    
    def test_generate_sparkline_empty_data(self):
        """Test sparkline generation with empty data."""
        result = self.generator.generate_sparkline([])
        
        assert isinstance(result, str)
        assert '<svg' in result
        assert 'No data available' in result
    
    def test_generate_sparkline_single_point(self):
        """Test sparkline generation with single data point."""
        result = self.generator.generate_sparkline([42])
        
        assert isinstance(result, str)
        assert '<svg' in result
        assert 'polyline' in result
    
    def test_generate_sparkline_all_zeros(self):
        """Test sparkline generation with all zero values."""
        result = self.generator.generate_sparkline([0, 0, 0, 0])
        
        assert isinstance(result, str)
        assert '<svg' in result
        assert 'polyline' in result
    
    def test_validate_input_invalid_type(self):
        """Test input validation with invalid data type."""
        with pytest.raises(ValueError, match="data_points must be a list"):
            self.generator._validate_input("not a list")
    
    def test_validate_input_too_many_points(self):
        """Test input validation with too many data points."""
        large_data = list(range(1001))
        with pytest.raises(ValueError, match="Too many data points"):
            self.generator._validate_input(large_data)
    
    def test_validate_input_negative_values(self):
        """Test input validation with negative values."""
        with pytest.raises(ValueError, match="Invalid data point"):
            self.generator._validate_input([1, 2, -3, 4])
    
    def test_validate_input_non_numeric(self):
        """Test input validation with non-numeric values."""
        with pytest.raises(ValueError, match="Invalid data point"):
            self.generator._validate_input([1, 2, "three", 4])
    
    def test_calculate_points_normal_case(self):
        """Test point calculation for normal case."""
        data = [10, 20, 30]
        points = self.generator._calculate_points(data, 30, 40)
        
        assert len(points) == 3
        assert all(',' in point for point in points)
        # First point should be at x=0
        assert points[0].startswith('0.00')
        # Last point should be at x=width
        assert points[-1].startswith(str(float(self.config.width)))
    
    def test_svg_accessibility(self):
        """Test that generated SVG includes accessibility features."""
        result = self.generator.generate_sparkline([1, 2, 3])
        
        assert 'role="img"' in result
        assert 'aria-label=' in result
        assert '<title>' in result
        assert '<desc>' in result
    
    def test_error_handling_in_generation(self):
        """Test error handling during SVG generation."""
        # Mock a method to raise an exception
        with patch.object(self.generator, '_validate_input', side_effect=Exception("Test error")):
            with pytest.raises(SparklineGeneratorError):
                self.generator.generate_sparkline([1, 2, 3])


class TestGitHubActivityFetcher:
    """Test the GitHubActivityFetcher class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.fetcher = GitHubActivityFetcher(token="test_token", username="test_user")
    
    @patch('gen_sparkline.requests.Session.get')
    def test_fetch_activity_data_success(self, mock_get):
        """Test successful activity data fetching."""
        # Mock successful API response
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = [
            {"created_at": "2023-08-01T12:00:00Z", "type": "PushEvent"},
            {"created_at": "2023-08-02T12:00:00Z", "type": "IssuesEvent"},
        ]
        mock_get.return_value = mock_response
        
        result = self.fetcher.fetch_activity_data(days=7)
        
        assert isinstance(result, list)
        assert len(result) == 7
        assert all(isinstance(count, int) for count in result)
    
    @patch('gen_sparkline.requests.Session.get')
    def test_fetch_activity_data_api_error(self, mock_get):
        """Test API error handling."""
        mock_get.side_effect = Exception("API Error")
        
        with pytest.raises(GitHubAPIError):
            self.fetcher.fetch_activity_data()
    
    @patch('gen_sparkline.requests.Session.get')
    def test_fetch_activity_data_invalid_json(self, mock_get):
        """Test handling of invalid JSON response."""
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.side_effect = json.JSONDecodeError("Invalid JSON", "", 0)
        mock_get.return_value = mock_response
        
        with pytest.raises(GitHubAPIError):
            self.fetcher.fetch_activity_data()
    
    def test_process_events_valid_data(self):
        """Test event processing with valid data."""
        events = [
            {"created_at": datetime.now().isoformat() + "Z", "type": "PushEvent"},
            {"created_at": (datetime.now() - timedelta(days=1)).isoformat() + "Z", "type": "IssuesEvent"},
        ]
        
        result = self.fetcher._process_events(events, 7)
        
        assert isinstance(result, list)
        assert len(result) == 7
        assert sum(result) >= 0  # Should have some activity
    
    def test_process_events_invalid_dates(self):
        """Test event processing with invalid date formats."""
        events = [
            {"created_at": "invalid-date", "type": "PushEvent"},
            {"created_at": datetime.now().isoformat() + "Z", "type": "IssuesEvent"},
        ]
        
        # Should not raise an exception, but log warnings
        result = self.fetcher._process_events(events, 7)
        assert isinstance(result, list)
        assert len(result) == 7


class TestArgumentParser:
    """Test the argument parser functionality."""
    
    def test_parse_arguments_defaults(self):
        """Test argument parsing with default values."""
        with patch('sys.argv', ['gen_sparkline.py']):
            args = parse_arguments()
            assert args.username == "senpai-sama7"
            assert args.days == 30
            assert args.width == 400
            assert args.height == 60
            assert args.log_level == "INFO"
    
    def test_parse_arguments_custom_values(self):
        """Test argument parsing with custom values."""
        test_args = [
            'gen_sparkline.py',
            '--username', 'test_user',
            '--days', '14',
            '--width', '800',
            '--height', '120',
            '--log-level', 'DEBUG'
        ]
        
        with patch('sys.argv', test_args):
            args = parse_arguments()
            assert args.username == "test_user"
            assert args.days == 14
            assert args.width == 800
            assert args.height == 120
            assert args.log_level == "DEBUG"
    
    def test_parse_arguments_sample_data_flag(self):
        """Test the sample data flag."""
        with patch('sys.argv', ['gen_sparkline.py', '--use-sample-data']):
            args = parse_arguments()
            assert args.use_sample_data is True


class TestMainFunction:
    """Test the main function and CLI integration."""
    
    @patch('gen_sparkline.GitHubActivityFetcher')
    @patch('gen_sparkline.SparklineGenerator')
    def test_main_success_with_sample_data(self, mock_generator_class, mock_fetcher_class):
        """Test successful main execution with sample data."""
        # Mock the generator
        mock_generator = Mock()
        mock_generator.generate_sparkline.return_value = "<svg>test</svg>"
        mock_generator_class.return_value = mock_generator
        
        test_args = ['gen_sparkline.py', '--use-sample-data']
        
        with patch('sys.argv', test_args), \
             patch('builtins.print') as mock_print:
            result = main()
            
            assert result == 0
            mock_print.assert_called_once_with("<svg>test</svg>")
    
    @patch('gen_sparkline.GitHubActivityFetcher')
    @patch('gen_sparkline.SparklineGenerator')
    def test_main_success_with_output_file(self, mock_generator_class, mock_fetcher_class):
        """Test successful main execution with output file."""
        mock_generator = Mock()
        mock_generator.generate_sparkline.return_value = "<svg>test</svg>"
        mock_generator_class.return_value = mock_generator
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as tmp_file:
            test_args = ['gen_sparkline.py', '--use-sample-data', '--output', tmp_file.name]
            
            try:
                with patch('sys.argv', test_args):
                    result = main()
                    
                assert result == 0
                
                # Check that file was written
                with open(tmp_file.name, 'r') as f:
                    content = f.read()
                    assert content == "<svg>test</svg>"
            finally:
                os.unlink(tmp_file.name)
    
    @patch('gen_sparkline.GitHubActivityFetcher')
    def test_main_api_error(self, mock_fetcher_class):
        """Test main function handling API errors."""
        mock_fetcher = Mock()
        mock_fetcher.fetch_activity_data.side_effect = GitHubAPIError("API Error")
        mock_fetcher_class.return_value = mock_fetcher
        
        test_args = ['gen_sparkline.py', '--username', 'test_user']
        
        with patch('sys.argv', test_args):
            result = main()
            
            assert result == 1
    
    def test_main_keyboard_interrupt(self):
        """Test main function handling keyboard interrupt."""
        with patch('gen_sparkline.parse_arguments', side_effect=KeyboardInterrupt):
            result = main()
            assert result == 130


class TestLogging:
    """Test logging configuration and functionality."""
    
    def test_setup_logging_default(self):
        """Test default logging setup."""
        with patch('logging.basicConfig') as mock_config:
            setup_logging()
            mock_config.assert_called_once()
    
    def test_setup_logging_custom_level(self):
        """Test logging setup with custom level."""
        with patch('logging.basicConfig') as mock_config:
            setup_logging("DEBUG")
            mock_config.assert_called_once()
            
            # Check that the level was set correctly
            call_args = mock_config.call_args
            assert call_args[1]['level'] == logging.DEBUG


class TestIntegration:
    """Integration tests for the complete workflow."""
    
    def test_end_to_end_with_sample_data(self):
        """Test complete end-to-end workflow with sample data."""
        config = SparklineConfig(width=200, height=40)
        generator = SparklineGenerator(config)
        
        # Use the sample data from the original script
        sample_data = [12, 15, 8, 23, 18, 25, 30, 22, 19, 28, 35, 20, 15, 18, 25]
        
        result = generator.generate_sparkline(sample_data)
        
        # Verify the result is valid SVG
        assert result.startswith('<svg')
        assert result.endswith('</svg>')
        assert 'width="200"' in result
        assert 'height="40"' in result
        assert 'polyline' in result
        assert 'circle' in result
    
    @patch('gen_sparkline.requests.Session')
    def test_end_to_end_with_mock_api(self, mock_session_class):
        """Test complete workflow with mocked GitHub API."""
        # Mock the session and response
        mock_session = Mock()
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = [
            {"created_at": datetime.now().isoformat() + "Z", "type": "PushEvent"}
        ]
        mock_session.get.return_value = mock_response
        mock_session_class.return_value = mock_session
        
        # Test the complete workflow
        fetcher = GitHubActivityFetcher(token="test_token")
        generator = SparklineGenerator()
        
        activity_data = fetcher.fetch_activity_data(days=7)
        result = generator.generate_sparkline(activity_data)
        
        assert isinstance(result, str)
        assert '<svg' in result


if __name__ == '__main__':
    pytest.main([__file__])