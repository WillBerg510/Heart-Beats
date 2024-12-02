import React from 'react';
import './App.css';
import PoolMethod from './PoolMethod';

class App extends React.Component {
  constructor() {
    super();
    this.state ={
      poolMethod: '',
      username: '',
    }
  }

  fetchInfo = async (route) => {
    try {
      const response = await fetch(`http://localhost:5000/${route}`);
      if (!response?.ok) throw Error('Did not receive expected data');
      const data = await response.json();
      this.setState({ username: data.username })
    } catch (error) {
      console.log(error);
    }
  }

  setPoolMethod = (method) => {
    this.setState({poolMethod: method});
  }

  componentDidMount = async () => {
    this.fetchInfo('initial_info')
  }

  render() {
    const { poolMethod, username } = this.state;
    return (
      <div className="App">
        <h1>HeartBeats</h1>
        <h2>{`Connected to ${username}`}</h2>
        <h2>Select song pool:</h2>
        <PoolMethod poolMethod={poolMethod} setPoolMethod={this.setPoolMethod}
          text="Your Top 100 Favorite Tracks"
          method="favTracks"
        />
        <PoolMethod poolMethod={poolMethod} setPoolMethod={this.setPoolMethod}
          text="Your Top 10 Favorite Artists"
          method="favArtists"
        />
        <PoolMethod poolMethod={poolMethod} setPoolMethod={this.setPoolMethod}
          text="Your Top 3 Genres"
          method="favGenres"
        />
        <p></p>
        <button>BEGIN</button>
      </div>
    );
  }
}

export default App;
