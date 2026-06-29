var appConfig = {
  ver: 1,
  title: "JSTV Demo",
  tabs: [
    {
      name: "Demo",
      ext: { type: "demo" },
    },
  ],
};

var videos = [
  {
    id: "bbb",
    name: "Big Buck Bunny",
    cover: "",
    remark: "Demo",
    url: "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4",
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
  for (var i = 0; i < videos.length; i++) {
    if (videos[i].id === id) return videos[i];
  }
  return null;
}

async function getConfig() {
  return toJson(appConfig);
}

async function getCards(ext) {
  return toJson({ list: videos.map(toCard) });
}

async function getTracks(ext) {
  var args = fromArgs(ext);
  var item = findVideo(args.id);
  if (!item) return toJson({ list: [] });
  return toJson({
    list: [
      {
        title: "Demo",
        tracks: [
          {
            name: "Play",
            pan: "",
            ext: { url: item.url },
          },
        ],
      },
    ],
  });
}

async function getPlayinfo(ext) {
  var args = fromArgs(ext);
  return toJson({
    urls: args.url ? [args.url] : [],
    headers: args.url ? [{ "User-Agent": "Mozilla/5.0" }] : [],
  });
}

async function search(ext) {
  var args = fromArgs(ext);
  var text = String(args.text || "").toLowerCase();
  var list = videos.filter(function (item) {
    return item.name.toLowerCase().indexOf(text) >= 0;
  });
  return toJson({ list: list.map(toCard) });
}

var api = {
  getConfig: getConfig,
  getCards: getCards,
  getTracks: getTracks,
  getPlayinfo: getPlayinfo,
  search: search,
};

if (typeof module !== "undefined") {
  module.exports = api;
  module.exports.default = api;
}
