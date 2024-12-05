import React from 'react';
import './App.css';
import PoolMethod from './PoolMethod';
import UsernameText from './UsernameText';
import HeartRateText from './HeartRateText';
import DataStructure from './DataStructure';
import CurrentlyPlaying from './CurrentlyPlaying';

class App extends React.Component {
  constructor() {
    super();
    this.state ={
      poolMethod: 0,
      loading: '',
      songsLoaded: false,
      structure: '',
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

  setStructure = (newStructure) => {
    this.setState({structure: newStructure});
  }

  begin = async () => {
    const { poolMethod, loading, structure } = this.state;
    if (loading == "Loading") return;
    if (poolMethod == 0) {
      this.setState({
        loading: "Please select a song pool."
      });
      return;
    }
    if (structure == '') {
      this.setState({
        loading: "Please select a data structure."
      });
      return;
    }
    this.setState({
      loading: "Loading..."
    })
    try {
      const response = await fetch('http://localhost:5000/begin', {
        method: "POST",
        body: JSON.stringify({
          pool: poolMethod,
          dataStructure: structure,
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
    }
    const interval = setInterval(async () => {
      const response = (await this.fetchInfo('http://localhost:5000/songs_loaded'))?.loaded;
      if (response) {
        this.setState({
          loading: '',
        })
        clearInterval(interval);
      }
    }, 500)
  }

  render() {
    const { poolMethod, loading, structure } = this.state;
    return (
      <div className="App">
        <h1>HeartBeats</h1>
        <UsernameText/>
        <h2>Select song pool:</h2>
        <PoolMethod poolMethod={poolMethod} setPoolMethod={this.setPoolMethod}
          text="Your Top 100 Favorite Tracks"
          method={1}
        />
        <h2>Select data structure:</h2>
        <DataStructure structure={structure} setStructure={this.setStructure}
          text="Graph"
        />
        <DataStructure structure={structure} setStructure={this.setStructure}
          text="Map"
        />
        <p></p>
        <button onClick={this.begin}>BEGIN</button>
        <p>{loading}</p>
        <HeartRateText/>
        <CurrentlyPlaying structure={structure}/>
      </div>
    );
  }
}

export default App;
