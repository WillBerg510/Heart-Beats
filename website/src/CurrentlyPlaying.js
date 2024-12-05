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
        {(structure == "Graph" && playing.otherSongs) && (<div>
          <p>Connected to these most similar songs:</p>
          {[0, 1, 2, 3, 4, 5, 6, 7, 8, 9].map((index) => (<>
            {(playing.otherSongs["id" + index]) && (<div>
              <p><b>{playing.otherSongs["id" + index].name}</b> by {playing.otherSongs["id" + index].artist} (BPM {playing.otherSongs["id" + index].bpm})</p>
              <img src={playing.otherSongs["id" + index].album_cover} height={60}/>
              </div>)}
            </>
          ))}
        </div>)}
        {(structure == "Map" && playing.otherSongs) && (<div>
          <p>Songs within the BPM range of the current heartbeat:</p>
          {[0, 1, 2, 3, 4, 5, 6, 7, 8, 9].map((index) => (<>
            {(playing.otherSongs["id" + index]) && (<div>
              <p><b>{playing.otherSongs["id" + index].name}</b> by {playing.otherSongs["id" + index].artist} (BPM {playing.otherSongs["id" + index].bpm})</p>
              <img src={playing.otherSongs["id" + index].album_cover} height={60}/>
              </div>)}
            </>
          ))}
        </div>)}
      </div>)}
    </>
  )
}

export default CurrentlyPlaying