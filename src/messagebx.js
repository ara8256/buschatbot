
import React from 'react';
import Message from './message';
import './messagebox.css';

const MessageBox = ({ messages }) => {
    return (
        <div className='d-flex justify-content-center'>
            <div className="message-box" style={{ backgroundColor: "#f0f8ff", borderRadius: "2vh" }}>
                {messages.map((msg, index) => (
                    <Message key={index} text={msg.text} sender={msg.sender} />
                ))}
            </div>
        </div>
    );
};

export default MessageBox;
