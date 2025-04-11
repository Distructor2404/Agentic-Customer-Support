import React, { useState, useEffect, useRef } from 'react';
import './RaiseTicket.css';
import { Send } from 'lucide-react';
import { FaRobot } from 'react-icons/fa';
import { PulseLoader } from 'react-spinners';
// import ReactMarkdown from 'react-markdown';
// import remarkGfm from 'remark-gfm'; // Import remark-gfm for tables support
// import remarkGemoji from "remark-gemoji";


function RaiseTicket() {
    const [messages, setMessages] = useState([]);
    const [inputMessage, setInputMessage] = useState('');
    const [ticketId, setTicketId] = useState(null);
    const [ticketCreated, setTicketCreated] = useState(false);
    const [sessionActive, setSessionActive] = useState(true);
    const [isLoading, setIsLoading] = useState(false);

    const messagesEndRef = useRef(null);

    // API endpoints
    const CREATE_TICKET_URL = "http://127.0.0.1:8001/customer-support/create-ticket";
    const CHAT_URL = "http://127.0.0.1:8001/customer-support/chat";

    // Scroll to bottom whenever messages change
    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    // Initial welcome message
    useEffect(() => {
        setMessages([
            {
                content: "Welcome to Agentic Customer Support! Please provide us the detailed issues that you are facing.",
                sender: "system"
            }
        ]);
    }, []);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    };

    const handleInputChange = (e) => {
        setInputMessage(e.target.value);
    };

    const handleSubmit = async (e) => {
        e.preventDefault();

        if (!inputMessage.trim()) return;

        // Add user message to chat
        setMessages(prev => [...prev, { content: inputMessage, sender: "user" }]);

        // Store message for processing
        const messageToProcess = inputMessage;
        setInputMessage('');

        if (!ticketCreated) {
            await createTicket(messageToProcess);
        } else {
            await sendChatMessage(messageToProcess);
        }
    };

    const createTicket = async (query) => {
        setIsLoading(true);
    
        // Add a loader message
        const loadingMsg = { content: "Creating your ticket...", sender: "system", loading: true };
        setMessages(prev => [...prev, loadingMsg]);
    
        try {
            const response = await fetch(CREATE_TICKET_URL, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ query })
            });
    
            const data = await response.json();
    
            // Remove loader message
            setMessages(prev => prev.filter(msg => !msg.loading));
    
            if (response.ok) {
                const newTicketId = data.ticket_id;
    
                if (newTicketId) {
                    setTicketId(newTicketId);
                    setTicketCreated(true);
    
                    setMessages(prev => [
                        ...prev,
                        {
                            content: `Ticket created successfully! Ticket ID: ${newTicketId}`,
                            sender: "system"
                        }
                    ]);
    
                    await sendChatMessage(query, newTicketId);
                } else {
                    setMessages(prev => [
                        ...prev,
                        {
                            content: "Error: No ticket ID returned from the server.",
                            sender: "system"
                        }
                    ]);
                }
            } else {
                const errorText = await response.text();
                setMessages(prev => [
                    ...prev,
                    {
                        content: `Error creating ticket: ${response.status} - ${errorText}`,
                        sender: "system"
                    }
                ]);
            }
        } catch (error) {
            setMessages(prev => [
                ...prev,
                {
                    content: `An error occurred: ${error.message}`,
                    sender: "system"
                }
            ]);
        } finally {
            setIsLoading(false);
        }
    };

    const sendChatMessage = async (query, passedTicketId = null) => {
        setIsLoading(true);
    
        // Add loading message
        const loadingMsg = { content: "Thinking...", sender: "system", loading: true };
        setMessages(prev => [...prev, loadingMsg]);
    
        try {
            const response = await fetch(CHAT_URL, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    query,
                    ticket_id: passedTicketId || ticketId,
                    user_id: "user_1",
                    query_id: "query_1"
                })
            });
    
            // Remove loader
            setMessages(prev => prev.filter(msg => !msg.loading));
    
            if (response.ok) {
                const data = await response.json();
                const responseText = data.data || "No response data available";
    
                setMessages(prev => [...prev, { content: responseText, sender: "system" }]);
            } else {
                const errorText = await response.text();
                setMessages(prev => [...prev, {
                    content: `Error: ${response.status} - ${errorText}`,
                    sender: "system"
                }]);
            }
        } catch (error) {
            setMessages(prev => [...prev, {
                content: `An error occurred: ${error.message}`,
                sender: "system"
            }]);
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div>
            <div className="chat-header">
                <h1>Agentic Customer Support</h1>
                <h2>Raise a ticket</h2>
                <div className="tooltip-container">
                    <button className="tooltip-button">What does this tool do?</button>
                    <div className="tooltip-text">
                        <strong>This tool uses AI Agents to provide smart customer support.</strong><br /><br />
                        Key features include:
                        <ul style={{ paddingLeft: '1rem', margin: 0 }}>
                            <br/>
                            <li>
                                <strong>Creating Ticket:</strong> Create Ticket based on the user requirements and help in resolving the issue.
                            </li>
                            <br/>
                            <li>
                                <strong>Update the ticket and notify support team:</strong> Update the ticket and inform customer support team about the ticket.
                            </li>
                            
                        </ul>
                    </div>
                </div>
            </div>
        <div className="chat-app">
            

            <div className="chat-messages">
                {messages.map((msg, index) => (
                    <div
                        key={index}
                        className={`message ${msg.sender === 'user' ? 'user-message' : 'system-message'}`}
                    >
                        {msg.sender === 'system' && (
                            <div className="bot-icon">
                                <FaRobot size={20} color="#d4076a" />
                            </div>
                        )}
                        <div className="message-content">
                            {msg.loading ? (
                                <PulseLoader color="#d4076a" size={10} />
                            ) : (
                                msg.content
                            )}
                        </div>
                    </div>
                ))}
                <div ref={messagesEndRef} />
            </div>

            <form className="chat-input" onSubmit={handleSubmit}>
                <input
                    type="text"
                    value={inputMessage}
                    onChange={handleInputChange}
                    placeholder="Type your message..."
                    disabled={isLoading}
                />
                <button
                    type="submit"
                    disabled={isLoading || !inputMessage.trim()}
                    className="send-button"
                >
                    <Send size={20} />
                </button>
            </form>
        </div>
        </div>
    );
}

export default RaiseTicket;