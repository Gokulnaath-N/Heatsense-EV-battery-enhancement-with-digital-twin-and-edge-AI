@echo off
setlocal
if "%HEATSENSE_DATASET_ROOT%"=="" (
  echo Set HEATSENSE_DATASET_ROOT before running this script.
  exit /b 1
)
echo Dataset root: %HEATSENSE_DATASET_ROOT%
echo.
echo Top-level entries:
dir "%HEATSENSE_DATASET_ROOT%"
echo.
echo Data directory sample:
dir "%HEATSENSE_DATASET_ROOT%\data" /b | more
echo.
echo This script only lists files. It does not modify the dataset.
endlocal
