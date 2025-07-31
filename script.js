const playButton = document.getElementById('playButton');
const songTitle = document.getElementById('songTitle');
const songMeta = document.getElementById('songMeta');
const cd = document.getElementById('cd');
const playlistDiv = document.getElementById('playlist');

let playlist = [];
let currentIndex = 0;
let audio = new Audio();

function getImageURL(songId) {
  return `https://radiooptimism.lg.com/images/${songId}_400x400.jpg`;
}

function getAudioURL(songId) {
  return `https://radiooptimism.lg.com/songs/${songId}.mp3`;
}

async function fetchPlaylist() {
  const res = await fetch('https://radiooptimism.lg.com/api/playlist?language_code=en-US');
  const data = await res.json();

  playlist = data.map(song => ({
    id: song.song_id,
    title: song.title || 'Untitled',
    sender: song.sender_name || '',
    recipient: song.recipient_name || '',
    image: getImageURL(song.song_id)
  }));
}

function updateVisualPlaylist() {
  playlistDiv.innerHTML = '';
  const nextSongs = playlist.slice(currentIndex + 1, currentIndex + 6);

  nextSongs.forEach(song => {
    const card = document.createElement('div');
    card.className = 'song-card';

    card.innerHTML = `
      <img src="${song.image}" alt="${song.title}" />
      <div class="song-card-title">${song.title}</div>
    `;

    playlistDiv.appendChild(card);
  });
}

function playNextSong() {
  if (currentIndex >= playlist.length) currentIndex = 0;

  const song = playlist[currentIndex];
  const audioURL = getAudioURL(song.id);

  audio.src = audioURL;
  audio.play();

  // Update UI
  songTitle.textContent = song.title;
  songMeta.textContent = `From: ${song.sender} → To: ${song.recipient}`;
  cd.src = song.image;
  cd.classList.add('rotate');

  updateVisualPlaylist();
  currentIndex++;

  audio.onended = () => {
    cd.classList.remove('rotate');
    playNextSong();
  };
}

playButton.addEventListener('click', async () => {
  if (playlist.length === 0) {
    await fetchPlaylist();
  }
  currentIndex = 0;
  playNextSong();
});
