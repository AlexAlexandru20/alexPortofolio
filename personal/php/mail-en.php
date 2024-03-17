<?php
if ($_SERVER["REQUEST_METHOD"] == "POST") {
    // Get form data
    $name = $_POST["name"];
    $second_name = $_POST["prenume"];
    $email = $_POST["email"];
    $subject = $_POST["subject"];
    $message = $_POST["message"];

    // Set up email parameters
    $to = "alexandrupopica18@gmail.com";
    $sender_subject = "Message from $name , $second_name";
    $sender_message = "Name: $name , $second_name\nEmail: $email\n\nMessage: $message";

    // Send email to recipient
    $recipient_email_sent = mail($to, $subject, $sender_message);

    // Send email to sender
    $sender_email = $email;
    $sender_subject = "Confirmation: Your message has been sent!";
    $sender_message = "Dear $name, $second_name\n\nThank you for your message. We have received it and will get back to you soon.\n\nBest regards,\nDigital Cyber";
    $sender_email_sent = mail($sender_email, $sender_subject, $sender_message);

    // Redirect back to the form page
    if ($recipient_email_sent && $sender_email_sent) {
        // Emails sent successfully
        echo "<script>
                alert('Message sent successfully!');
                window.location.href = 'https://digitalcyber-alex.liceultehnologicconstantinbrancusi.eu/index-en';
            </script>";
    } else {
        // Email sending failed
        echo "<script>
                alert('Message not sent. Please try again.');
                window.location.href = 'https://digitalcyber-alex.liceultehnologicconstantinbrancusi.eu/contact-en';
            </script>";
    }
    exit();
}
?>
