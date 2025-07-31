const playButton = document.getElementById('playButton');
const songTitle = document.getElementById('songTitle');
const songDesc = document.getElementById('songDesc');
const cd = document.getElementById('cd');
const playlistDiv = document.getElementById('playlist');

let playlist = [];
let currentIndex = 0;
let audio = new Audio();

async function fetchPlaylist() {
  const res = await fetch('https://radiooptimism.lg.com/api/playlist?language_code=en-US');
  const data = await res.json();

  const songIds = data.map(song => song.song_id);

  // Fetch full song info
  const infoPromises = songIds.map(async id => {
    try {
      const res = await fetch(`https://radiooptimism.lg.com/api/songs/info?id=${id}`);
      const info = await res.json();
      return {
        id,
        title: info.title || 'Unknown Title',
        desc: info.description || '',
        image: `https://radiooptimism.lg.com/images/${id}_400x400.jpg`
      };
    } catch (err) {
      return {
        id,
        title: 'Unknown Title',
        desc: '',
        image: 'https://via.placeholder.com/400x400?text=No+Image'
      };
    }
  });

  playlist = await Promise.all(infoPromises);
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
  const audioURL = `https://radiooptimism.lg.com/songs/${song.id}.mp3`;

  audio.src = audioURL;
  audio.play();

  // Update UI
  songTitle.textContent = song.title;
  songDesc.textContent = song.desc || 'No description available.';
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
