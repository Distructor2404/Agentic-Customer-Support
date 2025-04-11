import React, { useState, useEffect, useRef } from 'react';
import './Section.css';
import { Send } from 'lucide-react';
import { FaRobot } from 'react-icons/fa';
import { PulseLoader } from 'react-spinners';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm'; // Import remark-gfm for tables support
import remarkGemoji from "remark-gemoji";


function Section() {
    const [messages, setMessages] = useState([]);
    const [inputMessage, setInputMessage] = useState('');
    const [ticketId, setTicketId] = useState(null);
    const [ticketCreated, setTicketCreated] = useState(false);
    const [sessionActive, setSessionActive] = useState(true);
    const [isLoading, setIsLoading] = useState(false);

    const messagesEndRef = useRef(null);

    // API endpoints
    const CHAT_URL = "http://127.0.0.1:8001/customer-support/general-chat";

    

    // Scroll to bottom whenever messages change
    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    // Initial welcome message
    useEffect(() => {
        setMessages([
            {
                content: "Welcome to Agentic Customer Support!\nI can help with all the FAQs related to 'Hack the Future' and many more domain. Please check top right corner to know about me.  ",
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


        await sendChatMessage(messageToProcess);

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
                    ticket_id: "123",
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
                <h2>AI FAQs</h2>

                <div className="tooltip-container">
                    <button className="tooltip-button">What does this tool do?</button>
                    <div className="tooltip-text">
                        <strong>This tool uses AI Agents to provide smart customer support.</strong><br /><br />
                        Key features include:
                        <ul style={{ paddingLeft: '1rem', margin: 0 }}>
                            <br/>
                            <li>
                                <strong>Chat with website data:</strong> The agent uses advanced RAG (Retrieval-Augmented Generation). For example, it can answer FAQs from <strong><em>https://www.geeksforgeeks.org/accenture-data-and-ai-week</em></strong>. This can be customized for any site or company data.
                            </li>
                            <br/>
                            <li>
                                <strong>Chat with financial data:</strong> Users can interact with their own financial information. For instance, asking, “What were my last 3 transactions?”
                            </li>
                            <br/>
                            <li>
                                <strong>Fraud reporting:</strong> If a user marks a payment as fraudulent, the agent can automatically create a support ticket.
                            </li>
                            <br/>
                            <li>
                                <strong>Tool selection with memory:</strong> The AI agent autonomously selects the right tools for each query using long-term memory.
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
                                    <ReactMarkdown
                        remarkPlugins={[remarkGfm, remarkGemoji]}
                       
                      >
                                    {msg.content}
                                    </ReactMarkdown>

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

export default Section;