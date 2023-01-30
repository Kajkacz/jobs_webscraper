import { DashApp } from "dash-embedded-component";

window.React = React;
window.ReactDOM = ReactDOM;
window.PropTypes = PropTypes;

class App extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            sharedData: {
                myObject: {
                    clicks: 0,
                    aString: randomString(5),
                    data: myData,
                    // multiplyFunc: (x, y) => { ... },
                    // sumFunc: (x, y) => { ... },
                    // storeDataFromDash: obj => { ... },
                    // dashAppData: {}
                },
            },
        };
        this.clickIncrement = this.clickIncrement.bind(this);
        // ...
    }

    render() {
        return (
        <div className="App-Background">
            <div className="App-Content">
            <h1>Embedded Dash Application</h1>
            <DashApp config={ url_base_pathname: "http://dash.tests:8050" } value={this.state.sharedData} />
            </div>
        </div>
        );
    }
}