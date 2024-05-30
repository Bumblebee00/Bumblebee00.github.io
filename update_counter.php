<?php
$file = 'counter.txt';

if (!file_exists($file)) {
    $visit = 1;
} else {
    $visit = (int)file_get_contents($file) + 1;
}

file_put_contents($file, $visit);
?>