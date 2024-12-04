import React from 'react';
import './App.css';
import PoolMethod from './PoolMethod';
import UsernameText from './UsernameText';
import HeartRateText from './HeartRateText';

class App extends React.Component {
  constructor() {
    super();
    this.state ={
      poolMethod: 0,
      heartRate: '',
    }
  }

  fetchInfo = async (address) => {
    try {
      const response = await fetch(address);
      if (!response?.ok) throw Error('Did not receive expected data');
      const data = await response.json();
      return data;
    } catch (error) {
      console.log(error);
      return null;
    }
  }

  setPoolMethod = (method) => {
    this.setState({poolMethod: method});
  }

  begin = async () => {
    const { poolMethod } = this.state;
    await fetch('http://localhost:5000/begin', {
      method: "POST",
      body: JSON.stringify({
        pool: poolMethod,
      }),
      headers: {
        "Content-Type": "application/json"
      }
    })
  }

  render() {
    const { poolMethod, heartRate } = this.state;
    return (
      <div className="App">
        <h1>HeartBeats</h1>
        <UsernameText/>
        <h2>Select song pool:</h2>
        <PoolMethod poolMethod={poolMethod} setPoolMethod={this.setPoolMethod}
          text="Your Top 100 Favorite Tracks"
          method={1}
        />
        <PoolMethod poolMethod={poolMethod} setPoolMethod={this.setPoolMethod}
          text="Your Top 10 Favorite Artists"
          method={2}
        />
        <PoolMethod poolMethod={poolMethod} setPoolMethod={this.setPoolMethod}
          text="Your Top 3 Genres"
          method={3}
        />
        <p></p>
        <button onClick={this.begin}>BEGIN</button>
        <HeartRateText/>
      </div>
    );
  }
}

export default App;
