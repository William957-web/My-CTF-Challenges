<?php

if (isset($_GET['f'])){
        echo file_get_contents('/app/'.$_GET['f']);
}

if (isset($_GET['txt'])){
        echo "[+] Encrypting (length: " . strlen($_GET['txt']) . ")...\n";
        ob_start();
        $res = whale_encrypt($_GET['txt']);
        $out = ob_get_contents();
        ob_end_clean();
        echo "[+] Result length: " . strlen($res) . "\n";
        echo "[+] Result:".$res;
}
?>
