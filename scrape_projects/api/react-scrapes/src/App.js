import logo from './logo.svg';
import './App.css';

import React, { useState } from 'react';
import DateRangePicker from '@wojtekmaj/react-daterange-picker'

const now = new Date();
const yesterdayBegin = new Date(now.getFullYear(), now.getMonth(), now.getDate() - 1);
const todayEnd = new Date(now.getFullYear(), now.getMonth(), now.getDate(), 23, 59, 59, 999);

async function postData(url = '', data = {}) {
  // Default options are marked with *
  const response = await fetch(url, {
    method: 'POST', // *GET, POST, PUT, DELETE, etc.
    mode: 'cors', // no-cors, *cors, same-origin
    cache: 'no-cache', // *default, no-cache, reload, force-cache, only-if-cached
    credentials: 'same-origin', // include, *same-origin, omit
    headers: {
      'Content-Type': 'application/json'
      // 'Content-Type': 'application/x-www-form-urlencoded',
    },
    redirect: 'follow', // manual, *follow, error
    referrerPolicy: 'no-referrer', // no-referrer, *no-referrer-when-downgrade, origin, origin-when-cross-origin, same-origin, strict-origin, strict-origin-when-cross-origin, unsafe-url
    body: JSON.stringify(data) // body data type must match "Content-Type" header
  });
  return response.json(); // parses JSON response into native JavaScript objects
}


const App = () => {
  async function postDates() {
    return postData(
      "/valorant/matches-per-day.json", {
          date_begin: value[0],
          date_end: value[1]
        }
      )
    }
  
  const [value, onChange] = useState([yesterdayBegin, todayEnd]);
  
  return (
    <div>
      <DateRangePicker
        calendarAriaLabel="Toggle calendar"
        clearAriaLabel="Clear value"
        dayAriaLabel="Day"
        monthAriaLabel="Month"
        nativeInputAriaLabel="Date"
        onChange={onChange}
        value={value}
        yearAriaLabel="Year"
      />
      <p><button onClick={postDates}>Post!</button></p>
    </div>
  )
}

export default App;
