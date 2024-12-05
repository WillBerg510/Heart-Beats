import React, {useState, useEffect} from 'react';

const CurrentlyPlaying = ({ structure }) => {
  const [playing, setPlaying] = useState({}); 
  const [currentTime, setCurrentTime] = useState(new Date())

  const fetchInfo = async (address) => {
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

  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentTime(new Date());
    }, 1000)

    async function fetchData() {
      setPlaying(await fetchInfo('http://localhost:5000/song_information'));
    }
    
    fetchData();

    return () => clearInterval(interval);
  })

  return (
    <>
      {(playing && playing.thisSong?.name) && (<div>
          <p>Currently playing: <b>{playing.thisSong.name}</b> by {playing.thisSong.artist} (BPM {playing.thisSong.bpm})</p>
          <img src={playing.thisSong.album_cover} height={120}/>
        {(structure == "Graph" && playing.otherSongs[9]) && (<div>
          <p>Connected to these most similar songs:</p>
          <p><b>{playing.otherSongs[0].name}</b> by {playing.otherSongs[0].artist} (BPM {playing.otherSongs[0].bpm})</p>
          <img src={playing.otherSongs[0].album_cover} height={60}/>
          <p><b>{playing.otherSongs[1].name}</b> by {playing.otherSongs[1].artist} (BPM {playing.otherSongs[1].bpm})</p>
          <img src={playing.otherSongs[1].album_cover} height={60}/>
          <p><b>{playing.otherSongs[2].name}</b> by {playing.otherSongs[2].artist} (BPM {playing.otherSongs[2].bpm})</p>
          <img src={playing.otherSongs[2].album_cover} height={60}/>
          <p><b>{playing.otherSongs[3].name}</b> by {playing.otherSongs[3].artist} (BPM {playing.otherSongs[3].bpm})</p>
          <img src={playing.otherSongs[3].album_cover} height={60}/>
          <p><b>{playing.otherSongs[4].name}</b> by {playing.otherSongs[4].artist} (BPM {playing.otherSongs[4].bpm})</p>
          <img src={playing.otherSongs[4].album_cover} height={60}/>
          <p><b>{playing.otherSongs[5].name}</b> by {playing.otherSongs[5].artist} (BPM {playing.otherSongs[5].bpm})</p>
          <img src={playing.otherSongs[5].album_cover} height={60}/>
          <p><b>{playing.otherSongs[6].name}</b> by {playing.otherSongs[6].artist} (BPM {playing.otherSongs[6].bpm})</p>
          <img src={playing.otherSongs[6].album_cover} height={60}/>
          <p><b>{playing.otherSongs[7].name}</b> by {playing.otherSongs[7].artist} (BPM {playing.otherSongs[7].bpm})</p>
          <img src={playing.otherSongs[7].album_cover} height={60}/>
          <p><b>{playing.otherSongs[8].name}</b> by {playing.otherSongs[8].artist} (BPM {playing.otherSongs[8].bpm})</p>
          <img src={playing.otherSongs[8].album_cover} height={60}/>
          <p><b>{playing.otherSongs[9].name}</b> by {playing.otherSongs[9].artist} (BPM {playing.otherSongs[9].bpm})</p>
          <img src={playing.otherSongs[9].album_cover} height={60}/>
        </div>)}
      </div>)}
    </>
  )
}

export default CurrentlyPlaying