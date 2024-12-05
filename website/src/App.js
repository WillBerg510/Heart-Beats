import React from 'react';
import './App.css';
import PoolMethod from './PoolMethod';
import UsernameText from './UsernameText';
import HeartRateText from './HeartRateText';
import DataStructure from './DataStructure';
import CurrentlyPlaying from './CurrentlyPlaying';

class App extends React.Component {
  constructor() { // Create app object on website
    super();
    this.state ={
      poolMethod: 0,
      loading: '',
      songsLoaded: false,
      structure: '',
      playlistID: '',
    }
  }

  fetchInfo = async (address) => { // Make API call to backend server
    try {
      const response = await fetch(address);
      if (!response?.ok) throw Error('Did not receive expected data');
      const data = await response.json(); // Get data if request gives a response
      return data;
    } catch (error) { // Log error if API call is unsuccessful
      console.log(error);
      return null;
    }
  }

  setPoolMethod = (method) => {
    this.setState({poolMethod: method});
  }

  setStructure = (newStructure) => {
    this.setState({structure: newStructure});
  }

  changePlaylistID = (e) => {
    this.setState({playlistID: e.target.value});
  }

  makePlaylist = async () => {
    await this.fetchInfo('http://localhost:5000/make_playlist');
  }

  begin = async () => { // Code to run when the Begin button is clicked
    const { poolMethod, loading, structure, playlistID } = this.state;
    if (loading == "Loading") return;
    if (poolMethod == 0) { // If no pool is chosen, give message
      this.setState({
        loading: "Please select a song pool."
      });
      return;
    }
    if (structure == '') { // If no data structure is chosen, give message
      this.setState({
        loading: "Please select a data structure."
      });
      return;
    }
    this.setState({
      loading: "Loading..."
    })
    try { // Send API request with user's selections
      const response = await fetch('http://localhost:5000/begin', {
        method: "POST",
        body: JSON.stringify({
          pool: poolMethod,
          dataStructure: structure,
          IDofPlaylist: playlistID,
        }),
        headers: {
          "Content-Type": "application/json"
        }
      })
      if (!response?.ok) throw Error('Did not receive expected data');
    } catch (error) {
      console.log(error);
      this.setState({
        loading: "Unable to communicate with backend."
      })
      return
    }
    
    const interval = setInterval(async () => { // Wait for songs to be loaded, and then remove Loading... message
      const response = (await this.fetchInfo('http://localhost:5000/songs_loaded'))?.loaded;
      if (response) {
        this.setState({
          loading: '',
        })
        this.setState({songsLoaded: true});
        clearInterval(interval);
      }
    }, 500)
  }

  render() {
    const { poolMethod, loading, structure, songsLoaded } = this.state;
    return (
      <div className="App">
        <h1>HeartBeats</h1>
        <UsernameText/>
        <h2>Select song pool:</h2>
        <PoolMethod poolMethod={poolMethod} setPoolMethod={this.setPoolMethod}
          text="Your Top 50 Favorite Tracks"
          method={1}
        />
        <PoolMethod poolMethod={poolMethod} setPoolMethod={this.setPoolMethod}
          text="Playlist"
          method={2}
        />
        <input type="text" name="playlist_id" placeholder="Playlist ID" onChange={this.changePlaylistID}/>
        <h2>Select data structure:</h2>
        <DataStructure structure={structure} setStructure={this.setStructure}
          text="Graph"
        />
        <DataStructure structure={structure} setStructure={this.setStructure}
          text="Map"
        />
        <p></p>
        <button onClick={this.begin}>BEGIN</button>
        <p></p>
        {songsLoaded && (<button onClick={this.makePlaylist}>Create Playlist From Songs Played</button>)}
        <p>{loading}</p>
        <HeartRateText/>
        <CurrentlyPlaying structure={structure}/>
      </div>
    );
  }
}

export default App;
