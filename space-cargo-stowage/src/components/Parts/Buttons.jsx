import React from 'react';
import PropTypes from 'prop-types';
import '../../styles/parts1.css';  // New Design System (was "./Buttons.css")

function Button({ text, onClick, className }) {
    return (
        <button 
            className={`base-button ${className || ''}`}
            onClick={onClick}
        >
            {text}
        </button>
    );
}

Button.propTypes = {
    text: PropTypes.string.isRequired,
    onClick: PropTypes.func,
    className: PropTypes.string
};

Button.defaultProps = {
    onClick: () => {},
    className: ''
};

export default Button;