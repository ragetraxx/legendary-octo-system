const playButton = document.getElementById('playButton');
const songTitle = document.getElementById('songTitle');
const songMeta = document.getElementById('songMeta');
const cd = document.getElementById('cd');
const playlistDiv = document.getElementById('playlist');

let playlist = [];
let currentIndex = 0;
const audio = new Audio();

function getImageURL(id) {
  return `https://radiooptimism.lg.com/images/${id}_400x400.jpg`;
}
function getAudioURL(id) {
  return `https://radiooptimism.lg.com/songs/${id}.mp3`;
}

async function fetchPlaylist() {
  try {
    console.log('Fetching playlist...');
    const res = await fetch('https://radiooptimism.lg.com/api/playlist?language_code=en-US');
    if (!res.ok) throw new Error(`Playlist fetch error: ${res.status}`);
    const data = await res.json();
    playlist = data.map(song => ({
      id: song.song_id,
      title: song.title || 'Untitled',
      sender: song.sender_name || '',
      recipient: song.recipient_name || '',
      image: getImageURL(song.song_id)
    }));
    console.log('Playlist loaded:', playlist);
  } catch (err) {
    console.error('Error fetching playlist:', err);
    alert('Failed to load playlist: ' + err.message);
  }
}

function updateVisualPlaylist() {
  playlistDiv.innerHTML = '';
  const nextSongs = playlist.slice(currentIndex + 1, currentIndex + 6);
  nextSongs.forEach(song => {
    const card = document.createElement('div');
    card.className = 'song-card';
    card.innerHTML = `
      <img src="${song.image}" alt="${song.title}" />
      <div class="song-card-title">${song.title}</div>`;
    playlistDiv.appendChild(card);
  });
}

function playNextSong() {
  if (!playlist.length) return;

  if (currentIndex >= playlist.length) {
    console.log('Reached end of playlist, looping.');
    currentIndex = 0;
  }

  const song = playlist[currentIndex];
  const audioURL = getAudioURL(song.id);

  console.log('Playing:', song.title, audioURL);
  audio.src = audioURL;
  audio.play()
    .then(() => {
      songTitle.textContent = song.title;
      songMeta.textContent = `From: ${song.sender} → To: ${song.recipient}`;
      cd.src = song.image;
      cd.classList.add('rotate');
      updateVisualPlaylist();
      currentIndex++;
    })
    .catch(err => {
      console.error('Playback error:', err);
      alert('Cannot play audio: ' + err.message);
    });
}

audio.onended = () => {
  cd.classList.remove('rotate');
  playNextSong();
};

playButton.addEventListener('click', async () => {
  if (!playlist.length) await fetchPlaylist();
  currentIndex = 0;
  playNextSong();
});
