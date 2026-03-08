export type Locale = "zh" | "en";

type TranslationDict = Record<string, string>;

const en: TranslationDict = {
  // Nav
  "nav.title": "StoryBook Workshop",

  // Home
  "home.hero.subtitle": "AI-powered picture book creation for your children.",
  "home.hero.desc1": "Personalized stories, beautiful slides, videos, and more.",
  "home.hero.desc2":
    "Choose a topic, set your child\u2019s age, pick a style \u2014 and let AI craft a unique educational picture book in minutes.",
  "home.hero.cta": "Start Creating",
  "home.features.stories": "AI Stories",
  "home.features.video": "Video Books",
  "home.features.audio": "Audio Stories",
  "home.features.infographic": "Infographics",
  "home.footer": "StoryBook Workshop \u2014 Making learning magical",

  // Create — child
  "create.child.title": "About Your Child",
  "create.child.name": "Nickname",
  "create.child.name.optional": "(optional)",
  "create.child.name.placeholder": "e.g. Luna",
  "create.child.gender": "Gender",
  "create.child.gender.boy": "Boy",
  "create.child.gender.girl": "Girl",
  "create.child.gender.any": "Any",
  "create.child.age": "Age Range",
  "create.child.age.to": "to",
  "create.child.lang": "Language",

  // Create — content
  "create.content.title": "Content",
  "create.content.topic.tab": "Choose a Topic",
  "create.content.story.tab": "Tell Your Own Story",
  "create.content.topic.custom": "Or enter your own topic",
  "create.content.topic.placeholder": "e.g. Volcanoes, Robots, Pirates",
  "create.content.story.label": "Your Story",
  "create.content.story.placeholder":
    "Paste or type your story here. AI will adapt it for your child\u2019s age...",
  "create.content.chapters": "Chapters",
  "create.content.chapters.short": "3 (short)",
  "create.content.chapters.detailed": "10 (detailed)",

  // Create — products
  "create.products.title": "Output Products",
  "create.products.desc": "Select what to generate. Each product is created via NotebookLM.",

  // Product labels & descriptions
  "product.slides": "Slides",
  "product.slides.desc": "Presentation deck",
  "product.video": "Video",
  "product.video.desc": "Animated video",
  "product.audio": "Audio",
  "product.audio.desc": "Podcast-style story",
  "product.infographic": "Infographic",
  "product.infographic.desc": "Visual poster",
  "product.quiz": "Quiz",
  "product.quiz.desc": "Knowledge check",
  "product.flashcards": "Flashcards",
  "product.flashcards.desc": "Study cards",
  "product.mind_map": "Mind Map",
  "product.mind_map.desc": "Topic overview",

  // Product option labels
  "option.format": "Format",
  "option.length": "Length",
  "option.style": "Style",
  "option.orientation": "Orientation",
  "option.detail": "Detail",
  "option.difficulty": "Difficulty",
  "option.quantity": "Quantity",

  // Option values
  "option.detailed": "Detailed",
  "option.presenter": "Presenter",
  "option.default": "Default",
  "option.short": "Short",
  "option.explainer": "Explainer",
  "option.brief": "Brief",
  "option.deep_dive": "Deep Dive",
  "option.critique": "Critique",
  "option.debate": "Debate",
  "option.landscape": "Landscape",
  "option.portrait": "Portrait",
  "option.square": "Square",
  "option.concise": "Concise",
  "option.standard": "Standard",
  "option.easy": "Easy",
  "option.medium": "Medium",
  "option.hard": "Hard",
  "option.fewer": "Fewer",

  // Video styles
  "video.kawaii": "Kawaii (Cute)",
  "video.watercolor": "Watercolor",
  "video.anime": "Anime",
  "video.paper_craft": "Paper Craft",
  "video.classic": "Classic",
  "video.whiteboard": "Whiteboard",
  "video.heritage": "Heritage",
  "video.retro_print": "Retro Print",
  "video.auto": "Auto",

  // Audio lengths
  "audio.short": "Short (~5 min)",
  "audio.default": "Default (~15 min)",
  "audio.long": "Long (~25 min)",

  // Create page header
  "create.page.title": "Create Your Picture Book",
  "create.page.desc": "Configure your child\u2019s personalized story in a few simple steps.",
  "create.page.back": "Back",

  // Generate page header
  "generate.page.title": "Creating Your Book...",
  "generate.page.desc": "Sit tight! AI is crafting a personalized picture book.",
  "generate.page.back": "Back to Create",

  // Result page header
  "result.page.title": "Your Picture Book is Ready!",
  "result.page.back": "Create Another",

  // Validation & submit
  "error.topic.required": "Please select or enter a topic.",
  "error.story.required": "Please enter your story text.",
  "create.submitting": "Creating...",
  "create.submit": "Create Picture Book",

  // Generation progress
  "progress.title": "Generation Progress",
  "progress.working": "Working on it...",
  "progress.tip": "This may take a few minutes. NotebookLM products can take 2-5 minutes each.",
  "progress.view_results": "View Results",
  "progress.try_again": "Try Again",
  "progress.connection_lost": "Connection lost. Please check the job status.",

  // Results
  "result.products.title": "Generated Products",
  "result.status.ready": "Ready",
  "result.status.failed": "Failed",
  "result.status.generating": "Generating...",
  "result.download": "Download",
  "result.story.title": "Story (Markdown)",
  "result.story.hide": "Hide",
  "result.story.preview": "Preview",
  "result.story.download": "Download .md",
  "result.create_new": "Create New Book",
  "result.create_another": "Create Another Book",
  "result.topic": "Topic",
  "result.language": "Language",
  "result.language.zh": "Chinese",
  "result.language.en": "English",
  "result.not_found": "Job not found",
};

const zh: TranslationDict = {
  // Nav
  "nav.title": "\u7ed8\u672c\u5de5\u574a",

  // Home
  "home.hero.subtitle": "AI \u9a71\u52a8\u7684\u513f\u7ae5\u7ed8\u672c\u521b\u4f5c\u5e73\u53f0",
  "home.hero.desc1":
    "\u4e2a\u6027\u5316\u6545\u4e8b\u3001\u7cbe\u7f8e\u5e7b\u706f\u7247\u3001\u89c6\u9891\u3001\u97f3\u9891\u7b49\u591a\u79cd\u4ea7\u54c1",
  "home.hero.desc2":
    "\u9009\u62e9\u4e3b\u9898\u3001\u8bbe\u5b9a\u5e74\u9f84\u3001\u6311\u9009\u98ce\u683c \u2014 \u8ba9 AI \u5728\u51e0\u5206\u949f\u5185\u4e3a\u4f60\u7684\u5b69\u5b50\u521b\u4f5c\u4e00\u672c\u72ec\u7279\u7684\u6559\u80b2\u7ed8\u672c\u3002",
  "home.hero.cta": "\u5f00\u59cb\u521b\u4f5c",
  "home.features.stories": "AI \u6545\u4e8b",
  "home.features.video": "\u89c6\u9891\u7ed8\u672c",
  "home.features.audio": "\u6709\u58f0\u6545\u4e8b",
  "home.features.infographic": "\u4fe1\u606f\u56fe",
  "home.footer":
    "\u7ed8\u672c\u5de5\u574a \u2014 \u8ba9\u5b66\u4e60\u5145\u6ee1\u9b54\u6cd5",

  // Create — child
  "create.child.title": "\u5b69\u5b50\u4fe1\u606f",
  "create.child.name": "\u6635\u79f0",
  "create.child.name.optional": "\uff08\u53ef\u9009\uff09",
  "create.child.name.placeholder": "\u4f8b\u5982\uff1a\u5c0f\u660e",
  "create.child.gender": "\u6027\u522b",
  "create.child.gender.boy": "\u7537\u5b69",
  "create.child.gender.girl": "\u5973\u5b69",
  "create.child.gender.any": "\u4e0d\u9650",
  "create.child.age": "\u5e74\u9f84\u8303\u56f4",
  "create.child.age.to": "\u81f3",
  "create.child.lang": "\u8bed\u8a00",

  // Create — content
  "create.content.title": "\u5185\u5bb9",
  "create.content.topic.tab": "\u9009\u62e9\u4e3b\u9898",
  "create.content.story.tab": "\u8bb2\u8ff0\u4f60\u7684\u6545\u4e8b",
  "create.content.topic.custom":
    "\u6216\u8f93\u5165\u81ea\u5b9a\u4e49\u4e3b\u9898",
  "create.content.topic.placeholder":
    "\u4f8b\u5982\uff1a\u706b\u5c71\u3001\u673a\u5668\u4eba\u3001\u6d77\u76d7",
  "create.content.story.label": "\u4f60\u7684\u6545\u4e8b",
  "create.content.story.placeholder":
    "\u5728\u8fd9\u91cc\u8f93\u5165\u6216\u7c98\u8d34\u4f60\u7684\u6545\u4e8b\uff0cAI \u4f1a\u5e2e\u4f60\u6da6\u8272\u5e76\u9002\u914d\u5b69\u5b50\u7684\u5e74\u9f84\u6bb5...",
  "create.content.chapters": "\u7ae0\u8282\u6570",
  "create.content.chapters.short": "3\uff08\u7b80\u77ed\uff09",
  "create.content.chapters.detailed": "10\uff08\u8be6\u7ec6\uff09",

  // Create — products
  "create.products.title": "\u8f93\u51fa\u4ea7\u54c1",
  "create.products.desc":
    "\u9009\u62e9\u8981\u751f\u6210\u7684\u4ea7\u54c1\uff0c\u6bcf\u4e2a\u4ea7\u54c1\u901a\u8fc7 NotebookLM \u751f\u6210\u3002",

  // Product labels & descriptions
  "product.slides": "\u5e7b\u706f\u7247",
  "product.slides.desc": "\u6f14\u793a\u6587\u7a3f",
  "product.video": "\u89c6\u9891",
  "product.video.desc": "\u52a8\u753b\u89c6\u9891",
  "product.audio": "\u97f3\u9891",
  "product.audio.desc": "\u64ad\u5ba2\u5f0f\u6545\u4e8b",
  "product.infographic": "\u4fe1\u606f\u56fe",
  "product.infographic.desc": "\u53ef\u89c6\u5316\u6d77\u62a5",
  "product.quiz": "\u6d4b\u9a8c",
  "product.quiz.desc": "\u77e5\u8bc6\u95ee\u7b54",
  "product.flashcards": "\u95ea\u5361",
  "product.flashcards.desc": "\u5b66\u4e60\u5361\u7247",
  "product.mind_map": "\u601d\u7ef4\u5bfc\u56fe",
  "product.mind_map.desc": "\u4e3b\u9898\u6982\u89c8",

  // Product option labels
  "option.format": "\u683c\u5f0f",
  "option.length": "\u957f\u5ea6",
  "option.style": "\u98ce\u683c",
  "option.orientation": "\u65b9\u5411",
  "option.detail": "\u8be6\u7ec6\u5ea6",
  "option.difficulty": "\u96be\u5ea6",
  "option.quantity": "\u6570\u91cf",

  // Option values
  "option.detailed": "\u8be6\u7ec6",
  "option.presenter": "\u6f14\u8bb2\u8005",
  "option.default": "\u9ed8\u8ba4",
  "option.short": "\u7b80\u77ed",
  "option.explainer": "\u8bb2\u89e3",
  "option.brief": "\u7b80\u8981",
  "option.deep_dive": "\u6df1\u5ea6",
  "option.critique": "\u8bc4\u6790",
  "option.debate": "\u8fa9\u8bba",
  "option.landscape": "\u6a2a\u7248",
  "option.portrait": "\u7ad6\u7248",
  "option.square": "\u65b9\u5f62",
  "option.concise": "\u7cbe\u7b80",
  "option.standard": "\u6807\u51c6",
  "option.easy": "\u7b80\u5355",
  "option.medium": "\u4e2d\u7b49",
  "option.hard": "\u56f0\u96be",
  "option.fewer": "\u8f83\u5c11",

  // Video styles
  "video.kawaii": "\u5361\u54c7\u4f0a",
  "video.watercolor": "\u6c34\u5f69",
  "video.anime": "\u52a8\u6f2b",
  "video.paper_craft": "\u526a\u7eb8",
  "video.classic": "\u7ecf\u5178",
  "video.whiteboard": "\u767d\u677f",
  "video.heritage": "\u4f20\u7edf",
  "video.retro_print": "\u590d\u53e4\u5370\u5237",
  "video.auto": "\u81ea\u52a8",

  // Audio lengths
  "audio.short": "\u77ed\uff08\u7ea6 5 \u5206\u949f\uff09",
  "audio.default":
    "\u9ed8\u8ba4\uff08\u7ea6 15 \u5206\u949f\uff09",
  "audio.long": "\u957f\uff08\u7ea6 25 \u5206\u949f\uff09",

  // Create page header
  "create.page.title": "\u521b\u5efa\u4f60\u7684\u7ed8\u672c",
  "create.page.desc": "\u7b80\u5355\u51e0\u6b65\uff0c\u4e3a\u5b69\u5b50\u5b9a\u5236\u4e13\u5c5e\u6545\u4e8b\u3002",
  "create.page.back": "\u8fd4\u56de",

  // Generate page header
  "generate.page.title": "\u6b63\u5728\u521b\u5efa\u7ed8\u672c...",
  "generate.page.desc": "\u8bf7\u7a0d\u5019\uff01AI \u6b63\u5728\u4e3a\u4f60\u7684\u5b69\u5b50\u521b\u4f5c\u4e13\u5c5e\u7ed8\u672c\u3002",
  "generate.page.back": "\u8fd4\u56de\u521b\u5efa",

  // Result page header
  "result.page.title": "\u7ed8\u672c\u5df2\u5b8c\u6210\uff01",
  "result.page.back": "\u518d\u521b\u5efa\u4e00\u672c",

  // Validation & submit
  "error.topic.required":
    "\u8bf7\u9009\u62e9\u6216\u8f93\u5165\u4e00\u4e2a\u4e3b\u9898\u3002",
  "error.story.required":
    "\u8bf7\u8f93\u5165\u4f60\u7684\u6545\u4e8b\u5185\u5bb9\u3002",
  "create.submitting": "\u6b63\u5728\u521b\u5efa...",
  "create.submit": "\u521b\u5efa\u7ed8\u672c",

  // Generation progress
  "progress.title": "\u751f\u6210\u8fdb\u5ea6",
  "progress.working": "\u6b63\u5728\u5904\u7406...",
  "progress.tip":
    "\u8fd9\u53ef\u80fd\u9700\u8981\u51e0\u5206\u949f\u3002NotebookLM \u4ea7\u54c1\u6bcf\u4e2a\u53ef\u80fd\u9700\u8981 2-5 \u5206\u949f\u3002",
  "progress.view_results": "\u67e5\u770b\u7ed3\u679c",
  "progress.try_again": "\u91cd\u8bd5",
  "progress.connection_lost":
    "\u8fde\u63a5\u4e2d\u65ad\uff0c\u8bf7\u68c0\u67e5\u4efb\u52a1\u72b6\u6001\u3002",

  // Results
  "result.products.title": "\u751f\u6210\u7684\u4ea7\u54c1",
  "result.status.ready": "\u5df2\u5b8c\u6210",
  "result.status.failed": "\u5931\u8d25",
  "result.status.generating": "\u751f\u6210\u4e2d...",
  "result.download": "\u4e0b\u8f7d",
  "result.story.title":
    "\u6545\u4e8b\uff08Markdown\uff09",
  "result.story.hide": "\u6536\u8d77",
  "result.story.preview": "\u9884\u89c8",
  "result.story.download": "\u4e0b\u8f7d .md",
  "result.create_new": "\u521b\u5efa\u65b0\u7ed8\u672c",
  "result.create_another": "\u518d\u521b\u5efa\u4e00\u672c",
  "result.topic": "\u4e3b\u9898",
  "result.language": "\u8bed\u8a00",
  "result.language.zh": "\u4e2d\u6587",
  "result.language.en": "\u82f1\u6587",
  "result.not_found": "\u4efb\u52a1\u672a\u627e\u5230",
};

export const translations: Record<Locale, TranslationDict> = { en, zh };
