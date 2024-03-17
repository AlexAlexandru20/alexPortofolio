<?php
if(isset($_POST["submit"])){
    $mailto = "alexandrupopica18@gmail.com";
    $name = $_POST['name'];
    $fromemail = $_POST['email'];
    $fromphone = $_POST['phone'];
    $message = $_POST['sub'];
    $subjectcust = "Mesajul s-a trimis cu succes!";
    $subjectme = "Mail-ul a fost trimis de către" . $nume;
    $emailme = "Numele clientului: " . $name . "\n" . "Număr de telefon: " . $fromphone . "\n\n" . "Mesajul clientului: " . "\n" . $message;
    $emailcust = "Dragă " . $name . " am primit email-ul trimis și vom reveni cu un răspuns în cel mai scurt timp." . "\n" . "Cu stimă, Liceul Tehnologic Constantin Brâncuși";
    $header = "De la: " . $fromemail;
    $header2 = "De la: " . $mailto;
    $result1 = mail($mailto, $subjectme, $emailme, $header);
    $result2 = mail($fromemail, $subjectcust, $emailcust, $header2);
    if($result1 && $result2){
        header("Location: https://www.liceultehnologicconstantinbrancusi.eu/succes.html");
        exit();
    }
    else{
        echo "Mesajul nu s-a trimis! Vă rugăm să reveniți peste câteva momente." . "\n" . "Dacă acest lucru persistă, vă rugăm să ne anunțați la numărul de telefon afișat.";
    }
}
?>