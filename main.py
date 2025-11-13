"""
Hand-Based Volume Controller
Main entry point for the application
"""

import argparse
import sys
from src.volume_controller import VolumeController
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description='Control system volume using hand gestures'
    )
    parser.add_argument(
        '--no-audio',
        action='store_true',
        help='Run in demo mode without changing system volume'
    )
    parser.add_argument(
        '--camera',
        type=int,
        default=0,
        help='Camera device index (default: 0)'
    )
    parser.add_argument(
        '--width',
        type=int,
        default=640,
        help='Camera frame width (default: 640)'
    )
    parser.add_argument(
        '--height',
        type=int,
        default=480,
        help='Camera frame height (default: 480)'
    )
    return parser.parse_args()


def main():
    """Main application entry point"""
    args = parse_arguments()
    
    logger.info("Starting Hand-Based Volume Controller")
    logger.info(f"Audio control: {'Disabled' if args.no_audio else 'Enabled'}")
    
    try:
        controller = VolumeController(
            camera_id=args.camera,
            frame_width=args.width,
            frame_height=args.height,
            enable_audio=not args.no_audio
        )
        controller.run()
    except KeyboardInterrupt:
        logger.info("Application stopped by user")
    except Exception as e:
        logger.error(f"Application error: {e}", exc_info=True)
        sys.exit(1)
    finally:
        logger.info("Shutting down...")


if __name__ == "__main__":
    main()