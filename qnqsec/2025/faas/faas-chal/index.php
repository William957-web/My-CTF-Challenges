<?php
    $cmd = $_GET['cmd'];
    if (!isset($cmd)) {
        highlight_file(__FILE__) && die();
    }
    
    if (strpos($cmd, ";") !== False || strpos($cmd, "|") !== False || strpos($cmd, "$") !== False ||
    strpos($cmd, "`") !== False || strpos($cmd, "&") !== False || strpos($cmd, "\n") !== False ||
    strpos($cmd, ">") !== False || strpos($cmd, "<") !== False || strpos($cmd, "(") !== False ||
    strpos($cmd, ")") !== False || strpos($cmd, " ") !== False || strpos($cmd, "\r") !== False ||
    strpos($cmd, "+") !== False || strpos($cmd, "{") !== False || strpos($cmd, "}") !== False ||
    strpos($cmd, "[") !== False || strpos($cmd, "]") !== False) {
        die("Bad bad hacker :<");
    }
    
    $cmd = "find " . $cmd;
    system($cmd);
