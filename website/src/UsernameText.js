import React, {useState, useEffect} from 'react';

const UsernameText = ({ }) => {
  const [username, setUsername] = useState(''); 
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
      setUsername((await fetchInfo('http://localhost:5000/username'))?.username);
    }
    
    fetchData();

    return () => clearInterval(interval);
  })

  return (
    <p>Connected to <b>{username}</b></p>
  )
}

export default UsernameText