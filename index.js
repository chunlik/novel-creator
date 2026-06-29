// CatPawOpen / JSTV demo source.
// Demo-only content: public sample videos, no third-party site scraping.

const appConfig = {
  ver: 1,
  title: "JSTV學習源",
  tabs: [
    {
      name: "示範影片",
      ext: { type: "demo" },
    },
  ],
};

const videos = [
  {
    id: "bbb",
    name: "Big Buck Bunny",
    cover: "https://peach.blender.org/wp-content/uploads/title_anouncement.jpg",
    remark: "示範影片",
    content: "Blender Foundation 公開示範影片，用來測試 JSTV 列表、詳情與播放流程。",
    url: "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4",
  },
  {
    id: "sintel",
    name: "Sintel",
    cover: "https://durian.blender.org/wp-content/uploads/2010/05/sintel_poster.jpg",
    remark: "示範影片",
    content: "Blender Foundation 公開示範影片，用來測試搜尋與播放流程。",
    url: "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/Sintel.mp4",
  },
];

function toJson(value) {
  if (typeof jsonify === "function") return jsonify(value);
  return JSON.stringify(value);
}

function fromArgs(value) {
  if (typeof argsify === "function") return argsify(value);
  if (!value) return {};
  if (typeof value === "object") return value;
  try {
    return JSON.parse(value);
  } catch (e) {
    return {};
  }
}

function toCard(item) {
  return {
    vod_id: item.id,
    vod_name: item.name,
    vod_pic: item.cover,
    vod_remarks: item.remark,
    ext: { id: item.id },
  };
}

function findVideo(id) {
  return videos.find((item) => item.id === id);
}

async function getConfig() {
  return toJson(appConfig);
}

async function getCards(ext) {
  fromArgs(ext);
  return toJson({
    list: videos.map(toCard),
  });
}

async function getTracks(ext) {
  const args = fromArgs(ext);
  const item = findVideo(args.id);
  if (!item) return toJson({ list: [] });

  return toJson({
    list: [
      {
        title: "示範線路",
        tracks: [
          {
            name: "播放",
            pan: "",
            ext: { url: item.url },
          },
        ],
      },
    ],
  });
}

async function getPlayinfo(ext) {
  const args = fromArgs(ext);
  const url = args.url || "";

  return toJson({
    urls: url ? [url] : [],
    headers: url
      ? [
          {
            "User-Agent":
              "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
          },
        ]
      : [],
  });
}

async function search(ext) {
  const args = fromArgs(ext);
  const text = String(args.text || "").toLowerCase();
  const list = videos.filter((item) => {
    return (
      item.name.toLowerCase().includes(text) ||
      item.content.toLowerCase().includes(text)
    );
  });

  return toJson({
    list: list.map(toCard),
  });
}
