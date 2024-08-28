# Define the path to your Python script
$pythonScript = "email1.py"

# Define the path to your Python executable
$pythonExecutable = "python"

# Run the command in an infinite loop
$count = 1
while ($true) {
    echo "Running $pythonScript" $count
    $count = $count + 1
    & $pythonExecutable $pythonScript
    # Optional: Add a delay before the next execution
    Start-Sleep -Seconds 10
}

