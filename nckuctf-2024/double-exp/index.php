<?php
require "secret.php";
//$payload=$_GET['payload'];
$payload="a#\n./f";
if (strlen($payload)>6) die("Bad bad cat");
$result=shell_exec("./pwn_me ".$payload);
if ($result=="Meowing Whale"){
    echo $flag;
}
highlight_file("index.php");
