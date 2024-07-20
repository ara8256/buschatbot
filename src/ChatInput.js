import React, { useState } from 'react';
import "./input.css";
import 'bootstrap/dist/css/bootstrap.min.css';

const ChatInput = ({ onSendMessage }) => {
    const [inputValue, setInputValue] = useState('');

    const handleChange = (event) => {
        setInputValue(event.target.value);
    };

    const handleSubmit = (event) => {
        event.preventDefault();
        if (inputValue.trim() !== '') {
            onSendMessage(inputValue);
            setInputValue('');
        }
    };

    return (
        <div className="container mb-3">
            <div className="row justify-content-center">
                <div className="col-12 col-sm-10 col-md-8 col-lg-6 mt-3">
                    <form onSubmit={handleSubmit}>
                        <div className="d-flex align-items-center justify-content-between" style={{ borderRadius: "5vh", border: "1px solid #ccc", padding: "0.5rem", outline: "none"}}>
                            <input
                                type="text"
                                className="form-control flex-grow-1"
                                placeholder="Message"
                                value={inputValue}
                                onChange={handleChange}
                                style={{ background: "none", border: "none", fontSize: "1rem", outline: "none" }}
                            />
                            <button type="submit" className="send-button btn btn-link p-0 ml-2">
                                <svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor" xmlns="http://www.w3.org/2000/svg">
                                    <path d="M2 21L23 12L2 3V10L17 12L2 14V21Z" fill="currentColor"/>
                                </svg>
                            </button>
                        </div>
                    </form>
                </div>
            </div>
        </div>
    );
};

export default ChatInput;
