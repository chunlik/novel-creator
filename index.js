// JSTV / CatPawOpen learning source.
// This file uses only demo videos with clear public sample URLs.
// Replace DEMO_ITEMS with your own authorized API or media library.

let siteKey = "";
let siteType = 0;

const SOURCE_NAME = "JSTV學習源";

const DEMO_ITEMS = [
  {
    vod_id: "bbb",
    vod_name: "Big Buck Bunny",
    vod_pic: "https://peach.blender.org/wp-content/uploads/title_anouncement.jpg",
    vod_remarks: "示範影片",
    vod_year: "2008",
    vod_area: "Open Movie",
    vod_actor: "Blender Foundation",
    vod_director: "Sacha Goedegebure",
    vod_content:
      "這是 Blender Foundation 的公開示範影片，用來測試 JSTV 的列表、詳情與播放流程。",
    type_id: "demo",
    play_url:
      "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4",
  },
  {
    vod_id: "sintel",
    vod_name: "Sintel",
    vod_pic: "https://durian.blender.org/wp-content/uploads/2010/05/sintel_poster.jpg",
    vod_remarks: "示範影片",
    vod_year: "2010",
    vod_area: "Open Movie",
    vod_actor: "Blender Foundation",
    vod_director: "Colin Levy",
    vod_content:
      "這是另一支公開示範影片，可用來測試搜尋、分類與不同影片 ID 的 detail/play 流程。",
    type_id: "demo",
    play_url:
      "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/Sintel.mp4",
  },
];

function ok(data) {
  return JSON.stringify(data);
}

function findItem(id) {
  return DEMO_ITEMS.find((item) => item.vod_id === id);
}

function toListItem(item) {
  return {
    vod_id: item.vod_id,
    vod_name: item.vod_name,
    vod_pic: item.vod_pic,
    vod_remarks: item.vod_remarks,
  };
}

async function init(cfg) {
  siteKey = cfg?.skey || "";
  siteType = cfg?.stype || 0;
}

async function home(filter) {
  return ok({
    class: [
      {
        type_id: "demo",
        type_name: "示範影片",
      },
    ],
    filters: {},
  });
}

async function homeVod() {
  return ok({
    list: DEMO_ITEMS.map(toListItem),
  });
}

async function category(tid, pg, filter, extend) {
  const page = Number(pg || 1);
  const pageSize = 20;
  const items = DEMO_ITEMS.filter((item) => item.type_id === tid);

  return ok({
    page,
    pagecount: 1,
    limit: pageSize,
    total: items.length,
    list: items.map(toListItem),
  });
}

async function detail(id) {
  const item = findItem(id);
  if (!item) {
    return ok({ list: [] });
  }

  return ok({
    list: [
      {
        vod_id: item.vod_id,
        vod_name: item.vod_name,
        vod_pic: item.vod_pic,
        vod_remarks: item.vod_remarks,
        vod_year: item.vod_year,
        vod_area: item.vod_area,
        vod_actor: item.vod_actor,
        vod_director: item.vod_director,
        vod_content: item.vod_content,
        vod_play_from: SOURCE_NAME,
        vod_play_url: `播放$${item.play_url}`,
      },
    ],
  });
}

async function play(flag, id, flags) {
  return ok({
    parse: 0,
    url: id,
  });
}

async function search(wd, quick, pg) {
  const keyword = String(wd || "").trim().toLowerCase();
  const list = DEMO_ITEMS.filter((item) => {
    return (
      item.vod_name.toLowerCase().includes(keyword) ||
      item.vod_content.toLowerCase().includes(keyword)
    );
  });

  return ok({
    list: list.map(toListItem),
  });
}

export function __jsEvalReturn() {
  return {
    init,
    home,
    homeVod,
    category,
    detail,
    play,
    search,
  };
}
