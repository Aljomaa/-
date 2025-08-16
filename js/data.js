// Basic seed data and config for Thinking Islamic

window.TI_CONFIG = {
  siteName: "تفكير إسلامي",
  baseAudio: "https://cdn.thinkingislamic.com/audio", // TODO: replace with actual CDN/S3
  downloadBase: "https://cdn.thinkingislamic.com/packs", // TODO
  podcastBase: "https://cdn.thinkingislamic.com/podcast", // TODO
};

window.RECITERS = [
  { id: "minshawi", name: "محمد صديق المنشاوي", country: "مصر", quality: [128, 192] },
  { id: "husr", name: "محمود خليل الحصري", country: "مصر", quality: [128] },
  { id: "abdulbasit", name: "عبد الباسط عبد الصمد", country: "مصر", quality: [128, 192] },
  { id: "saad", name: "سعد الغامدي", country: "السعودية", quality: [128, 192] },
  { id: "afasy", name: "مشاري العفاسي", country: "الكويت", quality: [128, 192] },
];

// Minimal surah metadata (id, name, meccan/medinan, ayah count)
window.SURAHS = [
  { id: 1, name: "الفاتحة", type: "meccan", ayahs: 7 },
  { id: 2, name: "البقرة", type: "medinan", ayahs: 286 },
  { id: 18, name: "الكهف", type: "meccan", ayahs: 110 },
  { id: 36, name: "يس", type: "meccan", ayahs: 83 },
  { id: 55, name: "الرحمن", type: "medinan", ayahs: 78 },
  { id: 56, name: "الواقعة", type: "meccan", ayahs: 96 },
  { id: 67, name: "الملك", type: "meccan", ayahs: 30 },
  { id: 112, name: "الإخلاص", type: "meccan", ayahs: 4 },
];

window.TRENDING = [67, 56, 36, 55];

// Simple article seeds
window.ARTICLES = [
  { id: "quran", title: "فضل القرآن وتدبره", excerpt: "آيات وأحاديث في فضل القرآن وأثر التدبر.", url: "#" },
  { id: "sunnah", title: "منهج أهل السنة", excerpt: "أصول السنة واتباع الدليل.", url: "#" },
  { id: "aqeedah", title: "أسس العقيدة الصحيحة", excerpt: "أهم مسائل العقيدة من الكتاب والسنة.", url: "#" },
  { id: "talib", title: "دليل طالب العلم المبتدئ", excerpt: "كيف تبدأ وتتدرج في الطلب.", url: "#" },
];

// Podcasts: two series "تفكر في القرآن" و "تفكر في السنة"
window.PODCASTS = [
  {
    series: "تفكّر في القرآن",
    episodes: [
      { id: "q-001", title: "مدخل إلى التدبر", duration: "12:30", audio: "intro-tadabbur.mp3" },
      { id: "q-002", title: "معاني من سورة الملك", duration: "10:05", audio: "surah-almulk-reflections.mp3" },
    ]
  },
  {
    series: "تفكّر في السنة",
    episodes: [
      { id: "s-001", title: "منزلة السنة من الدين", duration: "09:40", audio: "status-of-sunnah.mp3" },
      { id: "s-002", title: "حديث جبريل وأركان الإيمان", duration: "14:10", audio: "hadith-jibreel.mp3" },
    ]
  }
];