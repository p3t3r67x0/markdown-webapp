import 'alpinejs'
import './styles.css'

import io from 'socket.io-client';

const scheme = window.location.protocol;
const host = window.location.host;
const url = scheme + "//api." + host;
// const url = 'https://api.reedo.me';

const socket = io(url);

socket.emit('loaded');

socket.on('my_response', function(data) {
  let initialCode = document.querySelector('#initial');

  if (initialCode) {
    initialCode.parentNode.removeChild(initialCode);
  }

  let outputDiv = document.querySelector('#output');
  let contentDiv = document.createElement('div');
  contentDiv.innerHTML = '<code class="break-all">' + data.data + '</code><br>';

  while (contentDiv.firstChild) {
    outputDiv.appendChild(contentDiv.firstChild);
  }
});

socket.on('done', function(data) {
  const format = document.querySelector('#format');
  const input = document.querySelector('#input');

  fetch(url + '/retrieve', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        file: data.file
      })
    })
    .then(res => res.blob())
    .then(data => {
      download(data);
    }).catch(error => {
      console.error('error message ', error);
    });
});

window.download = function(data) {
  const file = new Blob([data], {
    type: 'application/pdf'
  });

  // process to auto download it
  const fileURL = URL.createObjectURL(file);
  const link = document.createElement('a');
  link.href = fileURL;
  link.download = 'out.pdf';
  link.click();
  link.remove();
}

window.bindForm = function() {
  return {
    input: null,
    format: 'gfm',
    startConverter() {
      document.querySelector('#output').innerHTML = '';
      socket.emit('instance', this.format, this.input);
    }
  }
}
