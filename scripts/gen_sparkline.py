#!/usr/bin/env python3
"""
GitHub Activity Sparkline Generator

A production-ready script for generating SVG sparklines from GitHub activity data.
Includes comprehensive error handling, logging, input validation, and GitHub API integration.
"""

import json
import logging
import os
import sys
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any, Tuple
import requests
from dataclasses import dataclass
import argparse


@dataclass
class SparklineConfig:
    """Configuration for sparkline generation."""
    width: int = 400
    height: int = 60
    margin: int = 10
    stroke_width: int = 2
    point_radius: int = 3
    gradient_start: str = "#4facfe"
    gradient_end: str = "#00f2fe"
    opacity: float = 0.8


class GitHubAPIError(Exception):
    """Custom exception for GitHub API errors."""
    pass


class SparklineGeneratorError(Exception):
    """Custom exception for sparkline generation errors."""
    pass


class GitHubActivityFetcher:
    """Handles GitHub API interactions for activity data."""
    
    def __init__(self, token: Optional[str] = None, username: str = "senpai-sama7"):
        self.token = token or os.getenv("GITHUB_TOKEN")
        self.username = username
        self.base_url = "https://api.github.com"
        self.session = requests.Session()
        
        if self.token:
            self.session.headers.update({"Authorization": f"token {self.token}"})
        
        self.logger = logging.getLogger(__name__)
    
    def fetch_activity_data(self, days: int = 30) -> List[int]:
        """
        Fetch GitHub activity data for the specified number of days.
        
        Args:
            days: Number of days to fetch activity for
            
        Returns:
            List of activity counts per day
            
        Raises:
            GitHubAPIError: If API request fails
        """
        try:
            # Fetch events from GitHub API
            url = f"{self.base_url}/users/{self.username}/events"
            params = {"per_page": 100, "page": 1}
            
            self.logger.info(f"Fetching activity data for {self.username}")
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            events = response.json()
            
            # Process events into daily activity counts
            activity_by_date = self._process_events(events, days)
            
            self.logger.info(f"Successfully fetched {len(activity_by_date)} days of activity")
            return activity_by_date
            
        except requests.RequestException as e:
            self.logger.error(f"GitHub API request failed: {e}")
            raise GitHubAPIError(f"Failed to fetch GitHub activity: {e}")
        except json.JSONDecodeError as e:
            self.logger.error(f"Failed to parse GitHub API response: {e}")
            raise GitHubAPIError(f"Invalid JSON response from GitHub API: {e}")
    
    def _process_events(self, events: List[Dict[str, Any]], days: int) -> List[int]:
        """Process GitHub events into daily activity counts."""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # Initialize activity counts for each day
        activity_counts = [0] * days
        
        for event in events:
            try:
                event_date = datetime.fromisoformat(
                    event["created_at"].replace("Z", "+00:00")
                ).replace(tzinfo=None)
                
                if start_date <= event_date <= end_date:
                    day_index = (event_date - start_date).days
                    if 0 <= day_index < days:
                        activity_counts[day_index] += 1
                        
            except (KeyError, ValueError) as e:
                self.logger.warning(f"Skipping invalid event: {e}")
                continue
        
        return activity_counts


class SparklineGenerator:
    """Generates SVG sparklines from activity data."""
    
    def __init__(self, config: Optional[SparklineConfig] = None):
        self.config = config or SparklineConfig()
        self.logger = logging.getLogger(__name__)
    
    def generate_sparkline(self, data_points: List[int]) -> str:
        """
        Generate SVG sparkline from data points.
        
        Args:
            data_points: List of numeric values to plot
            
        Returns:
            SVG string representation of the sparkline
            
        Raises:
            SparklineGeneratorError: If generation fails
        """
        try:
            self._validate_input(data_points)
            
            if not data_points:
                return self._generate_empty_sparkline()
            
            # Calculate dimensions and scaling
            max_val = max(data_points) if max(data_points) > 0 else 1
            plot_height = self.config.height - (2 * self.config.margin)
            
            # Generate polyline points
            points = self._calculate_points(data_points, max_val, plot_height)
            polyline = " ".join(points)
            
            # Generate SVG
            svg = self._generate_svg(polyline, data_points, max_val, plot_height)
            
            self.logger.info(f"Generated sparkline with {len(data_points)} data points")
            return svg
            
        except Exception as e:
            self.logger.error(f"Sparkline generation failed: {e}")
            raise SparklineGeneratorError(f"Failed to generate sparkline: {e}")
    
    def _validate_input(self, data_points: List[int]) -> None:
        """Validate input data points."""
        if not isinstance(data_points, list):
            raise ValueError("data_points must be a list")
        
        if len(data_points) > 1000:
            raise ValueError("Too many data points (max 1000)")
        
        for i, point in enumerate(data_points):
            if not isinstance(point, (int, float)) or point < 0:
                raise ValueError(f"Invalid data point at index {i}: {point}")
    
    def _calculate_points(self, data_points: List[int], max_val: int, plot_height: int) -> List[str]:
        """Calculate SVG polyline points."""
        points = []
        
        for i, val in enumerate(data_points):
            if len(data_points) == 1:
                x = self.config.width / 2
            else:
                x = (i / (len(data_points) - 1)) * self.config.width
            
            y = self.config.height - self.config.margin - (val / max_val) * plot_height
            points.append(f"{x:.2f},{y:.2f}")
        
        return points
    
    def _generate_svg(self, polyline: str, data_points: List[int], max_val: int, plot_height: int) -> str:
        """Generate the complete SVG string."""
        # Calculate last point position for the indicator circle
        last_val = data_points[-1]
        last_y = self.config.height - self.config.margin - (last_val / max_val) * plot_height
        
        return f'''<svg width="{self.config.width}" height="{self.config.height}" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Activity sparkline">
  <title>GitHub Activity Sparkline</title>
  <desc>Daily activity over the last {len(data_points)} days</desc>
  <defs>
    <linearGradient id="sparkGradient" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" style="stop-color:{self.config.gradient_start};stop-opacity:{self.config.opacity}"/>
      <stop offset="100%" style="stop-color:{self.config.gradient_end};stop-opacity:{self.config.opacity}"/>
    </linearGradient>
  </defs>
  <polyline points="{polyline}" fill="none" stroke="url(#sparkGradient)" stroke-width="{self.config.stroke_width}" stroke-linecap="round" stroke-linejoin="round"/>
  <circle cx="{self.config.width - 5}" cy="{last_y:.2f}" r="{self.config.point_radius}" fill="{self.config.gradient_end}" opacity="{self.config.opacity}"/>
</svg>'''
    
    def _generate_empty_sparkline(self) -> str:
        """Generate an empty sparkline for when no data is available."""
        return f'''<svg width="{self.config.width}" height="{self.config.height}" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="No activity data">
  <title>No Activity Data</title>
  <desc>No activity data available</desc>
  <text x="{self.config.width/2}" y="{self.config.height/2}" text-anchor="middle" dominant-baseline="middle" font-family="Arial, sans-serif" font-size="12" fill="#666">No data available</text>
</svg>'''


def setup_logging(level: str = "INFO") -> None:
    """Configure logging for the application."""
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(sys.stderr),
            logging.FileHandler("sparkline_generator.log", mode="a")
        ]
    )


def parse_arguments() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Generate GitHub activity sparkline SVG",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        "--username", "-u",
        default="senpai-sama7",
        help="GitHub username (default: senpai-sama7)"
    )
    
    parser.add_argument(
        "--days", "-d",
        type=int,
        default=30,
        help="Number of days to include (default: 30)"
    )
    
    parser.add_argument(
        "--width", "-w",
        type=int,
        default=400,
        help="SVG width in pixels (default: 400)"
    )
    
    parser.add_argument(
        "--height", "-h",
        type=int,
        default=60,
        help="SVG height in pixels (default: 60)"
    )
    
    parser.add_argument(
        "--output", "-o",
        help="Output file path (default: stdout)"
    )
    
    parser.add_argument(
        "--log-level", "-l",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="INFO",
        help="Logging level (default: INFO)"
    )
    
    parser.add_argument(
        "--use-sample-data",
        action="store_true",
        help="Use sample data instead of GitHub API"
    )
    
    return parser.parse_args()


def main() -> int:
    """Main entry point."""
    try:
        args = parse_arguments()
        setup_logging(args.log_level)
        
        logger = logging.getLogger(__name__)
        logger.info("Starting sparkline generation")
        
        # Configure sparkline generator
        config = SparklineConfig(
            width=args.width,
            height=args.height
        )
        
        generator = SparklineGenerator(config)
        
        # Get activity data
        if args.use_sample_data:
            logger.info("Using sample data")
            data_points = [12, 15, 8, 23, 18, 25, 30, 22, 19, 28, 35, 20, 15, 18, 25]
        else:
            fetcher = GitHubActivityFetcher(username=args.username)
            data_points = fetcher.fetch_activity_data(args.days)
        
        # Generate sparkline
        svg_content = generator.generate_sparkline(data_points)
        
        # Output result
        if args.output:
            with open(args.output, "w", encoding="utf-8") as f:
                f.write(svg_content)
            logger.info(f"Sparkline saved to {args.output}")
        else:
            print(svg_content)
        
        logger.info("Sparkline generation completed successfully")
        return 0
        
    except (GitHubAPIError, SparklineGeneratorError) as e:
        logger.error(f"Application error: {e}")
        return 1
    except KeyboardInterrupt:
        logger.info("Operation cancelled by user")
        return 130
    except Exception as e:
        logger.exception(f"Unexpected error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())