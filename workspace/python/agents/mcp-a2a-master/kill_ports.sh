#!/bin/bash

# Script to kill processes using specific ports

echo "Killing processes on ports 10000, 10001, and 3000..."

# Port 10000
if lsof -ti:10000 > /dev/null 2>&1; then
    echo "Killing process on port 10000..."
    lsof -ti:10000 | xargs kill -9
    echo "Port 10000 freed"
else
    echo "No process found on port 10000"
fi

# Port 10001
if lsof -ti:10001 > /dev/null 2>&1; then
    echo "Killing process on port 10001..."
    lsof -ti:10001 | xargs kill -9
    echo "Port 10001 freed"
else
    echo "No process found on port 10001"
fi

# Port 3000
if lsof -ti:3000 > /dev/null 2>&1; then
    echo "Killing process on port 3000..."
    lsof -ti:3000 | xargs kill -9
    echo "Port 3000 freed"
else
    echo "No process found on port 3000"
fi

echo "Done!"
