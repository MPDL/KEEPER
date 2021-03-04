import React, { Component } from 'react';
import PropTypes from 'prop-types';

const propTypes = {
  text: PropTypes.string.isRequired,
  maxLength: PropTypes.number.isRequired,
  className: PropTypes.string
};

class ExpandText extends Component {
    constructor(props) {
        super(props);
        this.state = {
            showFull: false
        };
    }

    render() {
        let visibleText = null;
        if (this.state.showFull || this.props.text.length <= this.props.maxLength) {
            visibleText = this.props.text;
        } else {
            const firstHalf = this.props.text.substring(0, this.props.maxLength / 2);
            const secondHalf = this.props.text.substring(this.props.text.length - (this.props.maxLength / 2), this.props.text.length)
            visibleText = `${firstHalf}...${secondHalf}`;
        }
        const self = this;
        const clickHandler = () => {
            self.setState({showFull: !self.state.showFull});
        }
        return <span onClick={clickHandler} className={this.props.className}>{visibleText}</span>;
  }
}

ExpandText.defaultProps = {
  className: ""
};

ExpandText.propTypes = propTypes;

export default ExpandText;