



import React from 'react';
import './message.css';


const Message = ({ text, sender}) => {
    // const handleSpeak = () => {
    //     if ('speechSynthesis' in window) {
    //         const utterance = new SpeechSynthesisUtterance(text);
    //         utterance.lang = language;
    //         console.log(utterance.lang);
    //         window.speechSynthesis.speak(utterance);
    //     } else {
    //         alert('Sorry, your browser does not support text to speech!');
    //     }
    // };

    return (
        <div className={`message ${sender ? 'sender' : 'receiver'}`}>
            <div className="message-content">
                {text}
               
            </div>
        </div>
    );
};

export default Message;
