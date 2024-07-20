import logo from './logo.svg';
import './App.css';
import MessageBox from './messagebx';
import ChatInput from './ChatInput';
import { useState } from 'react';
import { useEffect } from 'react';
import 'bootstrap/dist/css/bootstrap.min.css';


function App() {

  const [text, setText] = useState('');
  const [messages, setMessages] = useState([]);
  const [responseMessage, setResponseMessage] = useState('');











  const handleSendMessage = (message) => {
    setText(message);
    const newMessage = { text: message, sender: true};
    setMessages((prevMessages) => [...prevMessages, newMessage]);
    sendMessageToServer(message);
};


useEffect(() => {
        if (responseMessage) {
            const newResponseMessage = { text: responseMessage, sender: false };
            setMessages((prevMessages) => [...prevMessages, newResponseMessage]);
        }
    }, [responseMessage]);






    const [chatState, setChatState] = useState({
      output_array: [],
      list_to_be_asked: ["name", "phone#", "arrival city", "departure city", "date", "time"],
      last_question: ''
    });
    // let chatState = {
    //   output_array: [],
    //   list_to_be_asked: ["name", "phone#", "arrival city", "departure city", "date", "time"],
    //   last_question: ''
    // };
    
    const sendMessageToServer = async (response) => {
      try {
        const res = await fetch('http://127.0.0.1:5000/chat', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ response, chat_state: chatState }),  // Pass chat_state in the request body
        });
    
        const data = await res.json();
        console.log(data);  // Log the entire response for debugging
    
        // Update chatState with the state from the server
        if (data.chat_state) {
          setChatState(data.chat_state);
        }

        console.log(chatState)
    
        // Handle both "next_question" and "message" fields in the response
        if (data.next_question) {
          setResponseMessage(data.next_question);
        } else if (data.message) {
          setResponseMessage(data.message);
        }
      } catch (error) {

    // const sendMessageToServer = async (response) => {
    //   try {
    //     const res = await fetch('http://127.0.0.1:5000/chat', {
    //       method: 'POST',
    //       headers: {
    //         'Content-Type': 'application/json',
    //       },
    //       body: JSON.stringify({ response }),  // This matches the expected key in the Flask code
    //     });
    
    //     const data = await res.json();
    //     console.log(data);  // Log the entire response for debugging
    
    //     // Handle both "next_question" and "message" fields in the response
    //     if (data.next_question) {
    //       setResponseMessage(data.next_question);
    //     } else if (data.message) {
    //       setResponseMessage(data.message);
    //     }
    //   } catch (error) {
        console.error('Error:', error);
      }
    };






















  return (
    <div className="App">
      <MessageBox messages={messages}/>
      <ChatInput onSendMessage={handleSendMessage} />
    </div>
  );
}

export default App;
