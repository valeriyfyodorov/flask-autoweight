#!/usr/bin/env python3
# The shebang above lets this file run as an executable script when called by
# `uv run start/intranet/test_plate_rec.py`.

# usage: test_plate_rec.py [-h] [--weight WEIGHT] [{north,south}]
# Capture scale camera images and test plate recognition.
# positional arguments:
#   {north,south}    Scale configuration name to test.
# options:
#   -h, --help       show this help message and exit
#   --weight WEIGHT  Weight passed to getPlatesNumbers. Must be >= 200 to run recognition.

import argparse  # Builds a small command-line interface for choosing the scale.
import sys  # Lets this script add the repository root to Python's import path.
import time  # Provides the timestamp used in saved image filenames.
from pathlib import Path  # Gives safer filesystem path handling than raw strings.

import cv2  # OpenCV is used only here to write captured images to disk.


# `__file__` is this script path:
#   /Users/valera/venprojs/flask-autoweight/start/intranet/test_plate_rec.py
# `.parents[2]` walks up to the repository root:
#   /Users/valera/venprojs/flask-autoweight
REPO_ROOT = Path(__file__).resolve().parents[2]

# When this file is executed directly, Python may not automatically know about
# the project package root. Adding it to `sys.path` makes `start.intranet`
# imports work from the requested command:
#   uv run start/intranet/test_plate_rec.py
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

# Import the real Flask-app module that contains `getPlatesNumbers`.
# This import must happen after `sys.path` is fixed above.
from start.intranet import defs  # noqa: E402


# All test output images are saved next to this test file, inside:
#   start/intranet/test_results
TEST_RESULTS_DIR = Path(__file__).resolve().parent / "test_results"


def parse_args():
    # Create the command-line parser used by this standalone script.
    parser = argparse.ArgumentParser(
        description="Capture scale camera images and test plate recognition."
    )

    # Optional positional argument for selecting which configured scale to test.
    # If no value is supplied, the script uses "north".
    # Valid choices come directly from defs.SCALES, so this stays aligned with
    # the production config.
    parser.add_argument(
        "scales_name",
        nargs="?",
        default="north",
        choices=sorted(defs.SCALES.keys()),
        help="Scale configuration name to test.",
    )

    # `getPlatesNumbers` exits early when weight is below 200 kg.
    # The default 1000 value guarantees that recognition runs during this test.
    parser.add_argument(
        "--weight",
        type=int,
        default=1000,
        help="Weight passed to getPlatesNumbers. Must be >= 200 to run recognition.",
    )

    # Parse `sys.argv` and return a namespace with:
    #   args.scales_name
    #   args.weight
    return parser.parse_args()


def save_image(path, image):
    # A `None` image means camera capture failed or returned no frame.
    # Raising here makes the test failure explicit instead of silently producing
    # an empty/missing output file.
    if image is None:
        raise RuntimeError(f"Cannot save {path}: camera returned no image")

    # `cv2.imwrite` returns True/False rather than raising on many write errors.
    # Convert that return value into a normal Python exception so failures are
    # visible in the terminal.
    if not cv2.imwrite(str(path), image):
        raise RuntimeError(f"Cannot save {path}: cv2.imwrite returned False")


def main():
    # Read command-line options before doing any camera or API work.
    args = parse_args()

    # Ensure the result folder exists. `parents=True` also creates missing parent
    # folders, and `exist_ok=True` avoids failing if the folder is already there.
    TEST_RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    # Use one timestamp for both front and rear images, so files from the same
    # recognition run are easy to identify as a pair.
    timestamp = time.strftime("%Y%m%d_%H%M%S")

    # Store the actual image paths that were written during this run.
    # This lets the final printout show exactly where the images are.
    saved_paths = {}

    # Save the original camera-reading function before temporarily replacing it.
    # `getPlatesNumbers` calls `defs.readRtspImage` internally, but it does not
    # return the captured images. Wrapping this function is how the test can save
    # those same images without changing production code.
    original_read_rtsp_image = defs.readRtspImage

    def saving_read_rtsp_image(scale_cam, *read_args, **read_kwargs):
        # Call the original production camera reader first.
        # This keeps the recognition behavior identical to normal app behavior.
        image = original_read_rtsp_image(scale_cam, *read_args, **read_kwargs)

        # Detect whether this camera config is the selected scale's front camera.
        # `is` is intentional here because `getPlatesNumbers` passes the exact
        # dictionary object from `defs.SCALES`.
        if scale_cam is defs.SCALES[args.scales_name]["cam_front"]:
            camera_name = "front"

        # Detect whether this camera config is the selected scale's rear camera.
        elif scale_cam is defs.SCALES[args.scales_name]["cam_rear"]:
            camera_name = "rear"

        # Fallback label for unexpected future camera calls.
        # `getPlatesNumbers` currently only reads front and rear cameras.
        else:
            camera_name = "camera"

        # Build a unique, readable output filename such as:
        #   20260709_212500_north_front.jpg
        path = TEST_RESULTS_DIR / f"{timestamp}_{args.scales_name}_{camera_name}.jpg"

        # Save the captured frame to disk immediately after it is read.
        save_image(path, image)

        # Remember this path for the final terminal output.
        saved_paths[camera_name] = path

        # Return the unchanged image back to `getPlatesNumbers`, so the normal
        # plate-recognition API call receives exactly the same frame.
        return image

    # Temporarily replace the camera reader used by `defs.getPlatesNumbers`.
    # This is a small monkey patch scoped to this script run.
    defs.readRtspImage = saving_read_rtsp_image

    try:
        # Run the real application function under test.
        # It will read front/rear images, call the plate API, normalize long
        # plate values, and return a `PlatesSet`.
        plates = defs.getPlatesNumbers(args.scales_name, weight=args.weight)

    finally:
        # Always restore the original function, even if camera capture or the API
        # raises an exception. This keeps the module clean for any later imports
        # in the same Python process.
        defs.readRtspImage = original_read_rtsp_image

    # Blank line for readability after the progress logs printed by defs.py.
    print("")

    # Show where the captured images were saved.
    print("Saved images:")

    # Print the front image path, or "not captured" if the function exited before
    # reading that camera, for example when --weight is below 200.
    print(f"  front: {saved_paths.get('front', 'not captured')}")

    # Print the rear image path, or "not captured" if rear capture did not happen.
    print(f"  rear:  {saved_paths.get('rear', 'not captured')}")

    # Blank line between saved-file output and recognition output.
    print("")

    # Show the plate numbers returned by `getPlatesNumbers`.
    print("Recognized plates:")

    # `plates.front` is the recognized front plate string, or empty string if no
    # plate was recognized.
    print(f"  front: {plates.front}")

    # `plates.rear` is the recognized rear plate string, or empty string if no
    # plate was recognized.
    print(f"  rear:  {plates.rear}")


# Only run `main` when this file is executed as a script.
# This prevents camera/API work from starting if another module imports this file.
if __name__ == "__main__":
    main()
