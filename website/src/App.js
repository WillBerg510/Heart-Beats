import React from 'react';
import './App.css';
import PoolMethod from './PoolMethod';

class App extends React.Component {
  constructor() {
    super();
    this.state ={
      poolMethod: '',
      username: '',
      playlists : '',
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

  componentDidMount = async () => {
    this.setState({
      username: (await this.fetchInfo('http://localhost:5000/initial_info')).username,
      playlists: (await this.fetchInfo('http://localhost:5000/get_playlists')),
    })
  }

  render() {
    const { poolMethod, username, playlists } = this.state;
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
        <p>{playlists}</p>
        <button>BEGIN</button>
      </div>
    );
  }
}

export default App;
