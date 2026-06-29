const appConfig = {
  ver: 1,
  title: "JSTV Demo",
  site: "https://commondatastorage.googleapis.com",
  tabs: [
    {
      name: "Demo",
      ext: {
        id: 1,
      },
    },
  ],
};

const videos = [
  {
    id: "bbb",
    name: "Big Buck Bunny",
    cover: "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/images/BigBuckBunny.jpg",
    remarks: "Demo",
    url: "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4",
  },
  {
    id: "sintel",
    name: "Sintel",
    cover: "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/images/Sintel.jpg",
    remarks: "Demo",
    url: "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/Sintel.mp4",
  },
];

async function getConfig() {
  return jsonify(appConfig);
}

async function getCards(ext) {
  ext = argsify(ext);
  const cards = videos.map((item) => {
    return {
      vod_id: item.id,
      vod_name: item.name,
      vod_pic: item.cover,
      vod_remarks: item.remarks,
      ext: {
        url: item.url,
      },
    };
  });

  return jsonify({
    list: cards,
  });
}

async function getTracks(ext) {
  ext = argsify(ext);

  return jsonify({
    list: [
      {
        title: "Default",
        tracks: [
          {
            name: "Play",
            pan: "",
            ext: {
              url: ext.url,
            },
          },
        ],
      },
    ],
  });
}

async function getPlayinfo(ext) {
  ext = argsify(ext);

  return jsonify({
    urls: [ext.url],
    headers: [
      {
        "User-Agent":
          "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
      },
    ],
  });
}

async function search(ext) {
  ext = argsify(ext);
  const text = String(ext.text || "").toLowerCase();
  const cards = videos
    .filter((item) => item.name.toLowerCase().includes(text))
    .map((item) => {
      return {
        vod_id: item.id,
        vod_name: item.name,
        vod_pic: item.cover,
        vod_remarks: item.remarks,
        ext: {
          url: item.url,
        },
      };
    });

  return jsonify({
    list: cards,
  });
}
