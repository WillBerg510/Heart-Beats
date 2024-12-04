import React, {useState, useEffect} from 'react';

const HeartRateText = ({ }) => {
  const [heartRate, setHeartRate] = useState(''); 
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
      console.log('a');
      setHeartRate((await fetchInfo('http://localhost:5000/heart_rate'))?.heartRate);
    }
    
    fetchData();

    return () => clearInterval(interval);
  })

  return (
    <p>Current Heart Rate: <b>{heartRate}</b></p>
  )
}

export default HeartRateText