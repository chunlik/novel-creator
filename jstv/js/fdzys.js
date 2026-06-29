const cheerio = createCheerio()
const CryptoJS = createCryptoJS()

const UA =
  'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'

const appConfig = {
  ver: 1,
  title: '饭搭子影视',
  site: 'https://fdzys.net',
  tabs: [
    { name: '电影', ext: { url: 'https://fdzys.net/movie' } },
    { name: '电视剧', ext: { url: 'https://fdzys.net/tv' } },
    { name: '动漫', ext: { url: 'https://fdzys.net/animation' } },
    { name: '综艺', ext: { url: 'https://fdzys.net/variety' } },
    { name: '体育', ext: { url: 'https://fdzys.net/sports' } },
    { name: '短剧', ext: { url: 'https://fdzys.net/short' } },
  ],
}

function abs(url) {
  if (!url) return ''
  if (/^https?:\/\//i.test(url)) return url
  if (url.startsWith('//')) return 'https:' + url
  if (url.startsWith('/')) return appConfig.site + url
  return appConfig.site + '/' + url
}

function textOf($, node) {
  return ($(node).text() || '').replace(/\s+/g, ' ').trim()
}

function pickAttr($, root, selectors, attr) {
  for (const sel of selectors) {
    const val = $(root).find(sel).attr(attr)
    if (val) return val
  }
  return ''
}

function pickText($, root, selectors) {
  for (const sel of selectors) {
    const val = textOf($, $(root).find(sel).first())
    if (val) return val
  }
  return ''
}

async function fetchHtml(url, referer = appConfig.site + '/') {
  return await $fetch.get(url, {
    headers: {
      'User-Agent': UA,
      'Referer': referer,
    },
  })
}

async function tryPageUrls(baseUrl, page) {
  if (page <= 1) {
    const res = await fetchHtml(baseUrl)
    return { url: baseUrl, html: res.data }
  }

  const candidates = [
    `${baseUrl}/page/${page}`,
    `${baseUrl}/page/${page}/`,
    `${baseUrl}?page=${page}`,
    `${baseUrl}?p=${page}`,
    `${baseUrl}/${page}`,
  ]

  for (const url of candidates) {
    try {
      const res = await fetchHtml(url)
      const html = res.data || ''
      if (html && html.length > 500) {
        return { url, html }
      }
    } catch (e) {}
  }

  const res = await fetchHtml(baseUrl)
  return { url: baseUrl, html: res.data }
}

function parseCardsFromHtml(html) {
  const $ = cheerio.load(html)
  const cards = []
  const seen = new Set()

  const itemSelectors = [
    'a[href^="/movie/"][title]',
    'a[href^="/tv/"][title]',
    'a[href^="/animation/"][title]',
    'a[href^="/variety/"][title]',
    'a[href^="/sports/"][title]',
    'a[href^="/short/"][title]',
    '.module-item',
    '.public-list-box',
    '.vodlist li',
    '.stui-vodlist li',
    '.video-card',
    '.product-item',
    '.item',
  ]

  function pushCard(href, title, cover, remarks) {
    href = abs(href)
    if (!href || !title) return
    if (
      !/\/(movie|tv|animation|variety|sports|short)\//.test(href) &&
      !/\/(movie|tv|animation|variety|sports|short)$/.test(href)
    ) {
      return
    }
    if (seen.has(href)) return
    seen.add(href)
    cards.push({
      vod_id: href,
      vod_name: title.trim(),
      vod_pic: abs(cover),
      vod_remarks: (remarks || '').trim(),
      ext: { url: href },
    })
  }

  // 1) 先抓直接帶 title 的連結
  $('a[href][title]').each((_, e) => {
    const href = $(e).attr('href') || ''
    const title = ($(e).attr('title') || '').trim()
    if (!/\/(movie|tv|animation|variety|sports|short)\//.test(href)) return

    const box = $(e).closest('li, .module-item, .public-list-box, .video-card, .item, article, .col')
    const cover =
      $(e).find('img').attr('data-src') ||
      $(e).find('img').attr('data-original') ||
      $(e).find('img').attr('src') ||
      box.find('img').attr('data-src') ||
      box.find('img').attr('data-original') ||
      box.find('img').attr('src') ||
      ''
    const remarks =
      pickText($, box, [
        '.module-item-text',
        '.jidi span',
        '.hdinfo span',
        '.module-item-note',
        '.module-item-caption',
        '.pic-text',
        '.remarks',
        '.note',
        '.text-muted',
      ]) || ''
    pushCard(href, title, cover, remarks)
  })

  // 2) 再抓常见卡片结构
  for (const itemSel of itemSelectors) {
    $(itemSel).each((_, e) => {
      const href = pickAttr($, e, [
        'a[href^="/movie/"]',
        'a[href^="/tv/"]',
        'a[href^="/animation/"]',
        'a[href^="/variety/"]',
        'a[href^="/sports/"]',
        'a[href^="/short/"]',
        'a[href]',
      ], 'href')

      const title =
        pickAttr($, e, [
          'a[title]',
          'img[alt]',
        ], 'title') ||
        pickAttr($, e, ['img[alt]'], 'alt') ||
        pickText($, e, ['.module-item-title', '.title', 'h3', 'h4', 'a[title]', 'a'])

      const cover = pickAttr($, e, ['img[data-src]', 'img[data-original]', 'img[src]'], 'data-src') ||
        pickAttr($, e, ['img[data-original]'], 'data-original') ||
        pickAttr($, e, ['img[src]'], 'src')

      const remarks = pickText($, e, [
        '.module-item-text',
        '.jidi span',
        '.hdinfo span',
        '.module-item-note',
        '.module-item-caption',
        '.pic-text',
        '.remarks',
        '.note',
      ])

      pushCard(href, title, cover, remarks)
    })
  }

  return cards
}

function decodePlayerUrl(url, encrypt) {
  if (!url) return ''
  let u = url
  if (encrypt === '1' || encrypt === 1) {
    try { u = unescape(u) } catch (e) {}
  } else if (encrypt === '2' || encrypt === 2) {
    try { u = unescape(base64Decode(u)) } catch (e) {}
  }
  return u
}

function base64Decode(str) {
  const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/='
  let output = ''
  let buffer = 0, accumulatedBits = 0
  str = String(str).replace(/[^A-Za-z0-9+/=]/g, '')
  for (let i = 0; i < str.length; i++) {
    const c = chars.indexOf(str.charAt(i))
    if (c < 0) continue
    buffer = (buffer << 6) | c
    accumulatedBits += 6
    if (accumulatedBits >= 8) {
      accumulatedBits -= 8
      const code = (buffer >> accumulatedBits) & 0xff
      if (code) output += String.fromCharCode(code)
    }
  }
  return output
}

async function getConfig() {
  return jsonify(appConfig)
}

async function getCards(ext) {
  ext = argsify(ext)
  const page = Number(ext.page || 1)
  const baseUrl = ext.url || appConfig.site
  const { html } = await tryPageUrls(baseUrl, page)
  return jsonify({ list: parseCardsFromHtml(html) })
}

async function getTracks(ext) {
  ext = argsify(ext)
  const url = ext.url
  const { data } = await fetchHtml(url)
  const html = data || ''
  const $ = cheerio.load(html)

  const lines = []
  const lineSeen = new Set()

  const routeNames = []
  $('.route-list a, .play-list-tab a, .module-tab-item, .anthology-tab a, .nav-tabs li, .tab-item').each((_, e) => {
    const name = textOf($, e)
    if (name) routeNames.push(name)
  })

  // 站點已知會顯示多個雲線路與多集列表
  const routeNodes = []
  $('a[href]').each((_, e) => {
    const href = $(e).attr('href') || ''
    const name = textOf($, e)
    if (/^\/(movie|tv|animation|variety|sports|short)\//.test(href) && /第|\d+/.test(name)) {
      routeNodes.push(e)
    }
  })

  // 依詳情頁固定結構：先是多條線路，再是每條線路的集數串列
  let currentRoute = ''
  const knownRouteNames = ['天堂云','无印云','优质云','如意云','量子云','红牛云','星河云','非凡云','无尽云','优酷云']
  $('body *').each((_, e) => {
    const name = textOf($, e)
    if (knownRouteNames.includes(name)) {
      currentRoute = name
      if (!lineSeen.has(currentRoute)) {
        lineSeen.add(currentRoute)
        lines.push({ title: currentRoute, tracks: [] })
      }
      return
    }

    const tag = (e.tagName || '').toLowerCase()
    if (tag !== 'a') return
    const href = $(e).attr('href') || ''
    if (!href) return
    if (!/^\/(movie|tv|animation|variety|sports|short)\//.test(href)) return

    const epName = name
    if (!epName || !/第|\d+$/.test(epName)) return

    if (!currentRoute) {
      currentRoute = '默认线路'
      if (!lineSeen.has(currentRoute)) {
        lineSeen.add(currentRoute)
        lines.push({ title: currentRoute, tracks: [] })
      }
    }

    const line = lines.find(v => v.title === currentRoute)
    if (!line) return
    const playUrl = abs(href)
    if (line.tracks.some(v => v.ext && v.ext.url === playUrl)) return
    line.tracks.push({
      name: epName,
      pan: '',
      ext: { url: playUrl },
    })
  })

  if (!lines.length) {
    const tracks = []
    $('a[href]').each((_, e) => {
      const href = $(e).attr('href') || ''
      const name = textOf($, e)
      if (/^\/(movie|tv|animation|variety|sports|short)\//.test(href) && name) {
        if (/立即播放|播放|第|\d+$/.test(name)) {
          tracks.push({
            name,
            pan: '',
            ext: { url: abs(href) },
          })
        }
      }
    })
    if (tracks.length) lines.push({ title: '默认线路', tracks })
  }

  return jsonify({ list: lines })
}

async function getPlayinfo(ext) {
  ext = argsify(ext)
  const playPage = ext.url
  const { data } = await fetchHtml(playPage)
  const html = data || ''
  const $ = cheerio.load(html)

  let playurl = ''
  let headers = { 'User-Agent': UA, 'Referer': playPage }

  // 1) 常见 MacCMS player_aaaa
  let m = html.match(/var\s+player_?aaaa?\s*=\s*(\{.*?\})/s)
  if (m) {
    try {
      const player = JSON.parse(m[1])
      playurl = decodePlayerUrl(player.url, player.encrypt)
      if (player.from) headers['X-From'] = String(player.from)
    } catch (e) {}
  }

  // 2) 直接抓 m3u8 / mp4
  if (!playurl) {
    const direct = html.match(/https?:\/\/[^"'\\\s]+?\.(m3u8|mp4)(\?[^"'\\\s]*)?/i)
    if (direct) playurl = direct[0]
  }

  // 3) iframe 二次解析
  if (!playurl) {
    const iframe = $('iframe').attr('src')
    if (iframe) {
      try {
        const iframeUrl = abs(iframe)
        const res = await fetchHtml(iframeUrl, playPage)
        const iframeHtml = res.data || ''

        let direct = iframeHtml.match(/https?:\/\/[^"'\\\s]+?\.(m3u8|mp4)(\?[^"'\\\s]*)?/i)
        if (direct) {
          playurl = direct[0]
          headers = { 'User-Agent': UA, 'Referer': iframeUrl }
        }

        if (!playurl) {
          let pm = iframeHtml.match(/var\s+player\s*=\s*"(.*?)"/)
          let rand = iframeHtml.match(/var\s+rand\s*=\s*"(.*?)"/)
          if (pm && rand) {
            try {
              function decrypt(text, key, iv) {
                let keyValue = CryptoJS.enc.Utf8.parse(key)
                let ivValue = CryptoJS.enc.Utf8.parse(iv)
                return CryptoJS.AES.decrypt(text, keyValue, {
                  iv: ivValue,
                  padding: CryptoJS.pad.Pkcs7,
                }).toString(CryptoJS.enc.Utf8)
              }
              const content = JSON.parse(decrypt(pm[1], 'VFBTzdujpR9FWBhe', rand[1]))
              playurl = content.url || ''
              headers = { 'User-Agent': UA, 'Referer': iframeUrl }
            } catch (e) {}
          }
        }
      } catch (e) {}
    }
  }

  // 4) 常见 data-url
  if (!playurl) {
    const d1 = html.match(/data-url=["']([^"']+)["']/i)
    if (d1) playurl = d1[1]
  }

  playurl = playurl ? playurl.trim() : ''

  return jsonify({
    urls: playurl ? [playurl] : [],
    headers: playurl ? [headers] : [],
  })
}

async function search(ext) {
  ext = argsify(ext)
  const text = encodeURIComponent(ext.text || '')
  const page = Number(ext.page || 1)
  const cards = []

  const candidates = [
    `${appConfig.site}/index.php/ajax/suggest?mid=1&wd=${text}`,
    `${appConfig.site}/index.php/vod/search/page/${page}/wd/${text}.html`,
    `${appConfig.site}/search/${text}`,
    `${appConfig.site}/search?wd=${text}`,
  ]

  for (const url of candidates) {
    try {
      const { data } = await fetchHtml(url)
      const raw = data || ''

      // suggest json
      if (typeof raw === 'string' && raw.trim().startsWith('[')) {
        try {
          const arr = JSON.parse(raw)
          for (const it of arr) {
            const href = abs(it.url || it.vod_url || it.link || '')
            const name = (it.name || it.vod_name || '').trim()
            if (!href || !name) continue
            cards.push({
              vod_id: href,
              vod_name: name,
              vod_pic: abs(it.pic || it.vod_pic || ''),
              vod_remarks: (it.remarks || it.vod_remarks || '').trim(),
              ext: { url: href },
            })
          }
          if (cards.length) break
        } catch (e) {}
      }

      // html search page
      const found = parseCardsFromHtml(raw)
      if (found.length) {
        cards.push(...found)
        break
      }
    } catch (e) {}
  }

  // 去重
  const seen = new Set()
  const list = cards.filter(it => {
    const k = it.vod_id || ''
    if (!k || seen.has(k)) return false
    seen.add(k)
    return true
  })

  return jsonify({ list })
}
