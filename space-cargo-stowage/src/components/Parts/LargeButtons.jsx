import React from 'react';
import PropTypes from 'prop-types';
import '../../styles/parts1.css';  // New Design System (was "./largebuttons.css")

function LargeButtons({ text, onClick, isActive, icon }) {
    return (
        <button 
            className={`btn btn-large ${isActive ? 'is-active' : ''}`} 
            onClick={onClick}
        >
            {icon && <span className="button-icon"> {icon}  </span>}
            {text}
        </button>
    );
}

LargeButtons.propTypes = {
    text: PropTypes.string.isRequired,
    onClick: PropTypes.func,
    isActive: PropTypes.bool,
    icon: PropTypes.element
};

LargeButtons.defaultProps = {
    onClick: () => {},
    isActive: false,
    icon: null
};

export default LargeButtons;