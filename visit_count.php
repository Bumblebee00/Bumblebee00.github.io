<?php
$file = 'count.txt';

// Check if the file exists
if (!file_exists($file)) {
    // If not, create it and initialize the count to 0
    file_put_contents($file, 0);
}

// Read the current count from the file
$count = file_get_contents($file);

// Increment the count
$count++;

// Write the new count back to the file
file_put_contents($file, $count);

// Output the count
echo $count;
?>