import React, { useState, useEffect, useRef } from 'react';
import { STTManager, STT_STATES } from './services/sttService';
import './App.css';

const API_BASE = 'https://haqdaar.onrender.com';

// Top Interactive Hero Slideshow Schemes
const HERO_SLIDES = [
  {
    id: 'pm_aasha',
    image: '/banners/slide1_pm_aasha.jpg',
    tag: {
      hi: 'न्यूनतम समर्थन मूल्य सुरक्षा • भारत सरकार',
      mr: 'किमान आधारभूत किंमत हमी • भारत सरकार',
      ta: 'குறைந்தபட்ச ஆதரவு விலை திட்டம் • இந்திய அரசு'
    },
    title: {
      hi: 'प्रधानमंत्री अन्नदाता आय संरक्षण अभियान (PM-AASHA)',
      mr: 'प्रधानमंत्री अन्नदाता उत्पन्न संरक्षण अभियान (PM-AASHA)',
      ta: 'பிரதம மந்திரி அன்னதாதா வருமான பாதுகாப்பு இயக்கம் (PM-AASHA)'
    },
    subtitle: {
      hi: 'किसानों को उनकी उपज का लाभकारी मूल्य सुनिश्चित करना (मूल्य समर्थन योजना PSS, PDPS व निजी खरीद PPPS)',
      mr: 'शेतकऱ्यांना त्यांच्या शेतीमालाला हमीभाव व योग्य मोबदला मिळवून देणारे राष्ट्रीय अभियान',
      ta: 'விவசாயிகளுக்கு அவர்களின் விளைபொருட்களுக்கு நியாயமான மற்றும் லாபகரமான விலை உறுதி'
    },
    askBtnText: {
      hi: '🎙️ PM-AASHA के बारे में पूछें',
      mr: '🎙️ PM-AASHA विषयी विचारा',
      ta: '🎙️ PM-AASHA பற்றி கேட்கவும்'
    },
    query: {
      hi: 'पीएम आशा (PM-AASHA) योजना क्या है और किसानों को समर्थन मूल्य का लाभ कैसे मिलता है?',
      mr: 'पीएम-आशा योजनेची माहिती आणि शेतकऱ्यांना हमीभाव कसा मिळतो?',
      ta: 'பிஎம்-ஆஷா (PM-AASHA) திட்டத்தின் விவரங்கள் மற்றும் நன்மைகள் என்ன?'
    }
  },
  {
    id: 'pkvy',
    image: '/banners/slide2_pkvy.jpg',
    tag: {
      hi: 'प्राकृतिक व जैविक कृषि प्रोत्साहन',
      mr: 'सेंद्रिय व नैसर्गिक शेती प्रोत्साहन',
      ta: 'பாரம்பரிய இயற்கை விவசாய இயக்கம்'
    },
    title: {
      hi: 'परंपरागत कृषि विकास योजना (PKVY)',
      mr: 'परंपरागत कृषी विकास योजना (PKVY)',
      ta: 'பாரம்பரிய வேளாண் வளர்ச்சித் திட்டம் (PKVY)'
    },
    subtitle: {
      hi: 'जैविक खेती समूहों (Clusters), मृदा स्वास्थ्य सुधार व जैविक प्रमाणीकरण हेतु प्रति हेक्टेयर ₹50,000 की वित्तीय सहायता',
      mr: 'सेंद्रिय शेती गट निर्मिती, माती आरोग्य सुधारणा व प्रमाणीकरणासाठी प्रति हेक्टरी ₹५०,००० चे अनुदान',
      ta: 'இயற்கை விவசாயக் குழுக்கள், மண்வள மேம்பாடு மற்றும் அங்கக சான்றிதழ் பெற ஹெக்டேருக்கு ₹50,000 உதவி'
    },
    askBtnText: {
      hi: '🎙️ PKVY जैविक खेती के बारे में पूछें',
      mr: '🎙️ PKVY सेंद्रिय शेतीविषयी विचारा',
      ta: '🎙️ PKVY இயற்கை விவசாயம் பற்றி கேட்கவும்'
    },
    query: {
      hi: 'परंपरागत कृषि विकास योजना (PKVY) के तहत जैविक खेती पर क्या सहायता मिलती है?',
      mr: 'परंपरागत कृषी विकास योजनेचे अनुदान आणि अटी काय आहेत?',
      ta: 'PKVY இயற்கை விவசாய திட்டத்தின் கீழ் என்ன மானியம் கிடைக்கிறது?'
    }
  },
  {
    id: 'pm_kmy',
    image: '/banners/slide3_pm_kmy.webp',
    tag: {
      hi: 'किसान वृद्धावस्था सामाजिक सुरक्षा',
      mr: 'शेतकरी वृद्धापकाळ सामाजिक सुरक्षा',
      ta: 'விவசாயிகள் முதியோர் சமூக பாதுகாப்பு'
    },
    title: {
      hi: 'प्रधानमंत्री किसान मानधन योजना (PM-KMY)',
      mr: 'प्रधानमंत्री किसान मानधन योजना (PM-KMY)',
      ta: 'பிரதம மந்திரி கிசான் மான்தன் யோஜனா (PM-KMY)'
    },
    subtitle: {
      hi: '60 वर्ष की आयु पूर्ण होने पर छोटे व सीमांत किसानों को ₹3,000 प्रतिमाह सुनिश्चित न्यूनतम पेंशन सुरक्षा',
      mr: 'वयाची ६० वर्षे पूर्ण झाल्यावर अल्प व अत्यल्प भूधारक शेतकऱ्यांना ₹३,००० मासिक पेन्शनची हमी',
      ta: '60 வயது பூர்த்தியடைந்த சிறு, குறு விவசாயிகளுக்கு மாதம் ₹3,000 உத்தரவாத ஓய்வூதியம்'
    },
    askBtnText: {
      hi: '🎙️ किसान पेंशन (PM-KMY) के बारे में पूछें',
      mr: '🎙️ शेतकरी पेन्शन (PM-KMY) विषयी विचारा',
      ta: '🎙️ கிசான் ஓய்வூதியம் (PM-KMY) பற்றி கேட்கவும்'
    },
    query: {
      hi: 'पीएम किसान मानधन योजना (PM-KMY) में ₹3,000 मासिक पेंशन के लिए कौन पात्र है?',
      mr: 'पीएम किसान मानधन योजनेत पेन्शनसाठी पात्रता काय आहे?',
      ta: 'பிஎம்-கேஎம்ஒய் (PM-KMY) ஓய்வூதிய திட்டத்தின் தகுதிகள் என்ன?'
    }
  }
];

const VERIFIED_SCHEMES = [
  {
    id: 'pm_kisan',
    category: {
      hi: 'वित्तीय सहायता',
      mr: 'आर्थिक सहाय्य',
      ta: 'நிதி உதவி'
    },
    name: {
      hi: 'पीएम किसान सम्मान निधि',
      mr: 'पीएम किसान सन्मान निधी',
      ta: 'பிஎம் கிசான் சம்மான் நிதி'
    },
    benefit: {
      hi: '₹6,000 वार्षिक सहायता (3 समान किस्तों में ₹2,000)',
      mr: '₹6,000 दरवर्षी (3 हप्त्यांमध्ये ₹2,000)',
      ta: 'ஆண்டுக்கு ₹6,000 (3 தவணைகளில் ₹2,000)'
    },
    eligibility: {
      hi: 'भूमिधारक किसान परिवार (e-KYC व बैंक खाता आधार लिंक अनिवार्य)',
      mr: 'जमीनधारक शेतकरी कुटुंबे (e-KYC व आधार लिंक आवश्यक)',
      ta: 'நிலம் வைத்திருக்கும் விவசாய குடும்பங்கள் (e-KYC கட்டாயம்)'
    },
    statusBadge: {
      hi: '✅ सत्यापित सरकारी योजना',
      mr: '✅ सत्यापित शासकीय योजना',
      ta: '✅ அங்கீகரிக்கப்பட்ட அரசு திட்டம்'
    },
    verified: true,
    query: {
      hi: 'पीएम किसान सम्मान निधि के लिए कौन पात्र है?',
      mr: 'पीएम किसान योजनेसाठी कोण पात्र आहे?',
      ta: 'பிஎம் கிசான் திட்டத்தின் தகுதிகள் என்ன?'
    },
    icon: '💰'
  },
  {
    id: 'jal_hauz_rajkisan',
    category: {
      hi: 'सिंचाई एवं जल संचयन',
      mr: 'सिंचन व जलसंधारण',
      ta: 'பாசனம் & நீர் சேமிப்பு'
    },
    name: {
      hi: 'जल हौज निर्माण अनुदान (राजस्थान)',
      mr: 'जल हौद बांधकाम अनुदान',
      ta: 'ஜல் ஹவுஸ் பாசன மானியம்'
    },
    benefit: {
      hi: '1,00,000 लीटर पक्के जल हौज पर लागत का 50% तक अनुदान',
      mr: '1 लाख लिटर क्षमतेच्या पक्क्या हौदासाठी 50% पर्यंत अनुदान',
      ta: '1 லட்சம் லிட்டர் நீர் தொட்டி கட்ட 50% வரை மானியம்'
    },
    eligibility: {
      hi: 'न्यूनतम 0.5 हेक्टेयर सिंचित भूमि, राजकिसान साथी पोर्टल पर आवेदन',
      mr: 'किमान 0.5 हेक्टर सिंचित जमीन व आवश्यक शासकीय नोंदणी',
      ta: 'குறைந்தபட்சம் 0.5 ஹெக்டேர் பாசன நிலம் மற்றும் அரசு பதிவு'
    },
    statusBadge: {
      hi: 'ℹ️ पोर्टल विवरण • पुष्टि आवश्यक',
      mr: 'ℹ️ पोर्टल माहिती • पडताळणी आवश्यक',
      ta: 'ℹ️ அரசு போர்டல் • சரிபார்ப்பு தேவை'
    },
    verified: false,
    query: {
      hi: 'राजस्थान में जल हौज निर्माण पर कितना अनुदान मिलता है?',
      mr: 'जल हौद अनुदानाचे नियम व अटी काय आहेत?',
      ta: 'விவசாய நீர் சேமிப்பு மற்றும் பாசன மானியங்கள் क्या हैं?'
    },
    icon: '💧'
  },
  {
    id: 'diggi_rajkisan',
    category: {
      hi: 'सिंचाई व नहरी क्षेत्र',
      mr: 'सिंचन व कालवा क्षेत्र',
      ta: 'பாசனம் & கால்வாய் பகுதி'
    },
    name: {
      hi: 'डिग्गी निर्माण अनुदान (राजस्थान)',
      mr: 'डिग्गी (शेततळे) बांधकाम अनुदान',
      ta: 'டிக்கி நீர் சேமிப்பு மானியம்'
    },
    benefit: {
      hi: '4,00,000 लीटर पक्की डिग्गी पर 75% से 85% तक अनुदान (पोर्टल विवरण)',
      mr: '4 लाख लिटर पक्क्या डिग्गीसाठी 75% ते 85% पर्यंत अनुदान',
      ta: '4 லட்சம் லிட்டர் டிக்கி கட்ட 75% முதல் 85% வரை மானியம்'
    },
    eligibility: {
      hi: 'नहरी सिंचित क्षेत्र में 0.5 हेक्टेयर भूमि, पूर्व प्रशासनिक स्वीकृति अनिवार्य',
      mr: 'कालवा सिंचन क्षेत्रात किमान 0.5 हेक्टर शेतजमीन, पूर्व मंजुरी आवश्यक',
      ta: 'கால்வாய் பாசன பகுதியில் 0.5 ஹெக்டேர் நிலம், முன் அனுமதி கட்டாயம்'
    },
    statusBadge: {
      hi: 'ℹ️ पोर्टल विवरण • पुष्टि आवश्यक',
      mr: 'ℹ️ पोर्टल माहिती • पडताळणी आवश्यक',
      ta: 'ℹ️ அரசு போர்டல் • சரிபார்ப்பு தேவை'
    },
    verified: false,
    query: {
      hi: 'राजस्थान में डिग्गी निर्माण अनुदान की क्या शर्तें हैं?',
      mr: 'डिग्गी अनुदानासाठी कोणती कागदपत्रे लागतात?',
      ta: 'டிக்கி மானியத்திற்கு தேவையான நிபந்தனைகள் என்ன?'
    },
    icon: '🏗️'
  },
  {
    id: 'farm_pond_rajkisan',
    category: {
      hi: 'वर्षा जल संचयन',
      mr: 'पावसाचे पाणी साठवण',
      ta: 'மழைநீர் சேகரிப்பு'
    },
    name: {
      hi: 'खेत तलाई (Farm Pond) योजना',
      mr: 'शेततळे (Farm Pond) योजना',
      ta: 'பண்ணைக் குட்டை திட்டம் (Farm Pond)'
    },
    benefit: {
      hi: 'कच्चे या प्लास्टिक लाइनिंग फार्म पोंड पर 60% से 70% तक अनुदान',
      mr: 'कच्चे किंवा प्लॅस्टिक अस्तरीकरण शेततळ्यासाठी 60% ते 70% अनुदान',
      ta: 'பண்ணைக்குட்டை அமைக்க 60% முதல் 70% வரை அரசு மானியம்'
    },
    eligibility: {
      hi: 'न्यूनतम 0.5 हेक्टेयर काश्त भूमि, न्यूनतम 400 घनमीटर क्षमता',
      mr: 'किमान 0.5 हेक्टर शेतजमीन व किमान 400 घनमीटर क्षमता',
      ta: 'குறைந்தபட்சம் 0.5 ஹெக்டேர் நிலம் மற்றும் 400 கன மீட்டர் குட்டை'
    },
    statusBadge: {
      hi: 'ℹ️ पोर्टल विवरण • पुष्टि आवश्यक',
      mr: 'ℹ️ पोर्टल माहिती • पडताळणी आवश्यक',
      ta: 'ℹ️ அரசு போர்டல் • சரிபார்ப்பு தேவை'
    },
    verified: false,
    query: {
      hi: 'खेत तलाई (Farm Pond) अनुदान की जानकारी क्या है?',
      mr: 'शेततळे (Farm Pond) अनुदानाची माहिती काय आहे?',
      ta: 'பண்ணைக் குட்டை மானிய விவரங்கள் என்ன?'
    },
    icon: '🌊'
  },
  {
    id: 'pmmvy',
    category: {
      hi: 'मातृत्व पोषण सहायता',
      mr: 'मातृत्व व पोषण सहाय्य',
      ta: 'தாய்மை & ஊட்டச்சத்து உதவி'
    },
    name: {
      hi: 'पीएम मातृ वंदना योजना (PMMVY 2.0)',
      mr: 'पीएम मातृ वंदना योजना (PMMVY 2.0)',
      ta: 'பிரதம மந்திரி மாத்ரு வந்தனா யோஜனா'
    },
    benefit: {
      hi: 'प्रथम शिशु पर ₹5,000 व द्वितीय कन्या शिशु पर ₹6,000 डीबीटी सहायता',
      mr: 'पहिल्या अपत्यासाठी ₹5,000 व दुसऱ्या कन्या अपत्यासाठी ₹6,000',
      ta: 'முதல் குழந்தைக்கு ₹5,000, 2-வது பெண் குழந்தைக்கு ₹6,000'
    },
    eligibility: {
      hi: 'गर्भवती व धात्री माताएं (आशा/आंगनवाड़ी कार्यकर्ता द्वारा सत्यापन)',
      mr: 'गरोदर व स्तनदा माता (आशा/अंगणवाडी सेविकेमार्फत नोंदणी)',
      ta: 'கர்ப்பிணித் தாய்மார்கள் (ஆஷா / அங்கன்வாடி மூலம் பதிவு)'
    },
    statusBadge: {
      hi: '✅ सत्यापित सरकारी योजना',
      mr: '✅ सत्यापित शासकीय योजना',
      ta: '✅ அங்கீகரிக்கப்பட்ட அரசு திட்டம்'
    },
    verified: true,
    query: {
      hi: 'पीएम मातृ वंदना योजना (PMMVY) की पात्रता क्या है?',
      mr: 'पीएम मातृ वंदना योजनेचे लाभ काय आहेत?',
      ta: 'பிஎம் மாத்ரு வந்தனா யோஜனா திட்டத்தின் தகுதிகள் என்ன?'
    },
    icon: '🤱'
  }
];

const UI_STRINGS = {
  hi: {
    appTitle: 'हकदार',
    appSubTitle: 'HAQDAAR',
    tagline: 'ग्रामीण भारत का प्रामाणिक बहुभाषी आवाज़ सहायक',
    badgeText: 'डिजिटल जन सेवा • ICAR एवं सरकारी स्रोत',
    kisanTab: '🌾 किसान सहायक',
    kisanSub: 'कृषि, बीज व सिंचाई सलाह',
    yojanaTab: '🏛️ योजना सहायक',
    yojanaSub: 'सरकारी योजना व अनुदान',
    ashaTab: '🩺 आशा सहायक',
    ashaSub: 'मातृ-शिशु पोषण व स्वास्थ्य योजना',
    kisanDesc: 'फसलों की उन्नत तकनीक, बीज दर और कीट नियंत्रण की प्रमाणित ICAR सलाह',
    yojanaDesc: 'राजस्थान व केंद्रीय सरकारी योजनाओं की पात्रता, दस्तावेज और अधिकृत अनुदान',
    ashaDesc: 'मातृ व शिशु पोषण, टीकाकरण और सरकारी स्वास्थ्य सहायता योजनाओं की प्रमाणित जानकारी',
    schemesHeading: 'आज की प्रमुख सरकारी योजनाएँ',
    schemesSub: 'प्रमाणित व पोर्टल विवरण • पूरी जानकारी हेतु कार्ड पर टैप करें',
    viewDetailsBtn: 'पूरी जानकारी ➔',
    checkEligibilityBtn: 'पात्रता जांचें 📋',
    recentHeading: 'हाल में पूछे गए सवाल:',
    clearChatBtn: 'बातचीत साफ़ करें',
    clearConfirmTitle: 'क्या आप बातचीत साफ़ करना चाहते हैं?',
    clearConfirmDesc: 'यह सभी पिछले सवालों और उत्तरों को हटा देगा।',
    confirmYes: 'हाँ, साफ़ करें',
    confirmNo: 'रद्द करें',
    copyBtn: 'कॉपी करें 📋',
    copiedBtn: 'कॉपी हो गया! ✅',
    highContrastLabel: 'उच्च कंट्रास्ट',
    textSizeLabel: 'अक्षर आकार',
    micStart: 'बोलने के लिए माइक दबाएं',
    micListening: 'सुन रहा हूँ... अपनी बात कहिए',
    micProcessing: 'पहचान की जा रही है...',
    micStopHint: 'बोलने के बाद रोकें दबाएं या रुकें',
    inputLabel: 'आपका प्रश्न (जांचें व सुधारें)',
    inputPlaceholder: 'यहाँ अपना प्रश्न लिखें या माइक से बोलें...',
    sendBtn: 'पूछें ➔',
    speakBtn: 'उत्तर सुनें 🔊',
    pauseBtn: 'आवाज़ रोकें ⏹️',
    audioPlaying: 'सहायक बोल रहा है...',
    stopAudioBtn: '⏹️ आवाज़ बंद करें',
    sourceLabel: 'सत्यापित अधिकृत स्रोत',
    clearBtn: 'साफ़ करें',
    quickHeading: 'सुझाए गए सवाल:',
    welcomeGreeting: 'नमस्ते! हकदार में आपका स्वागत है।',
    welcomeSub: 'कृषि सलाह, सरकारी योजना या मातृ-स्वास्थ्य से जुड़ा कोई भी सवाल बोलकर पूछें।',
    heroVoiceTitle: 'अपनी भाषा में बोलकर पूछें',
    heroVoiceSubtitle: 'माइक दबाएं और फसलों, योजनाओं या स्वास्थ्य सहायता पर बेझिझक सवाल करें',
    disclaimer: '⚠️ यह जानकारी केवल मार्गदर्शन हेतु है। वित्तीय अनुदान व अंतिम स्वीकृति संबंधित सरकारी विभाग द्वारा नियमानुसार की जाएगी।',
    officialDisclaimer: '⚠️ योजना पात्रता, वर्तमान अनुदान राशि व दिशा-निर्देशों की अंतिम पुष्टि संबंधित विभाग के अधिकृत पोर्टल पर अवश्य करें।',
    healthDisclaimer: '⚠️ यह केवल सरकारी मातृत्व पोषण व स्वास्थ्य योजनाओं की प्रमाणित जानकारी है। चिकित्सीय निदान, दवा या आपातकाल हेतु तुरंत निकटतम PHC अथवा आशा कार्यकर्ता से संपर्क करें।',
    kvkHelpline: '📞 राष्ट्रीय किसान कॉल सेंटर: 1800-180-1551 (निःशुल्क) • निकटतम KVK या कृषि अधिकारी से संपर्क करें',
    languageSpeakGuidance: '🎙️ आप हिंदी, मराठी या तमिल में सीधे बोलकर पूछ सकते हैं',
    kisanPrompts: [
      'बाजरे की बुवाई का समय और बीज दर क्या है?',
      'सरसों की उन्नत किस्में और सिंचाई कब करें?',
      'गेहूं की DBW 187 और DBW 222 किस्मों की विशेषता क्या है?',
      'चने की फसल में फली छेदक कीट का जैविक नियंत्रण कैसे करें?'
    ],
    yojanaPrompts: [
      'राजस्थान में जल हौज निर्माण पर कितना अनुदान मिलता है?',
      'पीएम किसान सम्मान निधि के लिए कौन पात्र है?',
      'खेत तलाई (Farm Pond) अनुदान की क्या शर्तें हैं?',
      'राजस्थान में डिग्गी निर्माण अनुदान की क्या पात्रता है?'
    ],
    ashaPrompts: [
      'पीएम मातृ वंदना योजना (PMMVY) में ₹6,000 की सहायता कैसे मिलती है?',
      'गर्भवती महिलाओं के लिए आवश्यक पोषण और आहार सलाह क्या है?',
      'जननी सुरक्षा योजना (JSY) के तहत संस्थागत प्रसव पर क्या लाभ है?',
      'शिशु के जन्म के पहले वर्ष में आवश्यक टीकाकरण का समय क्या है?'
    ]
  },
  mr: {
    appTitle: 'हकदार',
    appSubTitle: 'HAQDAAR',
    tagline: 'ग्रामीण नागरिकांसाठी अधिकृत बहुभाषिक आवाज सहाय्यक',
    badgeText: 'डिजिटल जनसेवा • ICAR व शासकीय माहिती',
    kisanTab: '🌾 किसान सहायक',
    kisanSub: 'शेती, बियाणे व सिंचन सल्ला',
    yojanaTab: '🏛️ योजना सहायक',
    yojanaSub: 'शासकीय योजना व अनुदान',
    ashaTab: '🩺 आशा सहायक',
    ashaSub: 'माता-बाल पोषण व आरोग्य योजना',
    kisanDesc: 'पिकांचे आधुनिक तंत्रज्ञान, बियाणे प्रमाण व सिंचनाचा प्रमाणित ICAR सल्ला',
    yojanaDesc: 'शासकीय योजनांची खरी पात्रता, आवश्यक कागदपत्रे आणि अधिकृत अनुदान',
    ashaDesc: 'माता व बाल पोषण, लसीकरण आणि शासकीय आरोग्य योजनांची अधिकृत माहिती',
    schemesHeading: 'आजच्या प्रमुख शासकीय योजना',
    schemesSub: 'प्रमाणित व पोर्टल माहिती • तपशीलासाठी कार्डवर टॅप करा',
    viewDetailsBtn: 'सविस्तर माहिती ➔',
    checkEligibilityBtn: 'पात्रता तपासा 📋',
    recentHeading: 'नुकतेच विचारलेले प्रश्न:',
    clearChatBtn: 'संभाषण हटवा',
    clearConfirmTitle: 'तुम्हाला संभाषण हटवायचे आहे का?',
    clearConfirmDesc: 'हे मागील सर्व प्रश्न आणि उत्तरे काढून टाकेल.',
    confirmYes: 'होय, हटवा',
    confirmNo: 'रद्द करा',
    copyBtn: 'कॉपी करा 📋',
    copiedBtn: 'कॉपी झाले! ✅',
    highContrastLabel: 'हाय कॉन्ट्रास्ट',
    textSizeLabel: 'अक्षर आकार',
    micStart: 'बोलण्यासाठी माइक दाबा',
    micListening: 'ऐकत आहे... बोला',
    micProcessing: 'माहिती तपासत आहे...',
    micStopHint: 'बोलून झाल्यावर थांबवा दाबा किंवा थांबा',
    inputLabel: 'आपला प्रश्न (तपासा व सुधारणा करा)',
    inputPlaceholder: 'येथे प्रश्न लिहा किंवा माइकने बोला...',
    sendBtn: 'विचारा ➔',
    speakBtn: 'उत्तर ऐका 🔊',
    pauseBtn: 'थांबवा ⏹️',
    audioPlaying: 'सहाय्यक बोलत आहे...',
    stopAudioBtn: '⏹️ आवाज थांबवा',
    sourceLabel: 'अधिकृत प्रमाणित स्रोत',
    clearBtn: 'हटवा',
    quickHeading: 'सुचवलेले प्रश्न:',
    welcomeGreeting: 'नमस्कार! हकदार मध्ये आपले स्वागत आहे.',
    welcomeSub: 'शेती सल्ला, सरकारी योजना किंवा आरोग्य योजनांविषयी कोणताही प्रश्न बोलून विचारा.',
    heroVoiceTitle: 'आपल्या भाषेत थेट बोलून विचारा',
    heroVoiceSubtitle: 'माइक दाबा आणि शेती, सरकारी योजना किंवा माता-बाल पोषणावर बोला',
    disclaimer: '⚠️ ही माहिती केवळ मार्गदर्शनासाठी आहे. अंतिम मंजुरी सक्षम सरकारी विभागाकडूनच दिली जाईल.',
    officialDisclaimer: '⚠️ योजना पात्रता, अनुदान रक्कम व नियमांची अंतिम पडताळणी संबंधित अधिकृत पोर्टलवर करणे आवश्यक आहे.',
    healthDisclaimer: '⚠️ ही केवळ शासकीय मातृत्व पोषण व आरोग्य योजनांची प्रमाणित माहिती आहे. उपचारासाठी जवळच्या PHC अथवा आशा सेविकेशी संपर्क साधा.',
    kvkHelpline: '📞 किसान कॉल सेंटर: 1800-180-1551 (टोल फ्री) • जवळच्या KVK किंवा कृषी अधिकाऱ्याशी संपर्क साधा',
    languageSpeakGuidance: '🎙️ तुम्ही हिंदी, मराठी किंवा तमिळमध्ये थेट बोलून विचारू शकता',
    kisanPrompts: [
      'बाजरी पेरणीची वेळ आणि बियाणे प्रमाण किती?',
      'मोहरीच्या सुधारित जाती व सिंचन कधी करावे?',
      'गहू पिकातील DBW जातींची वैशिष्ट्ये काय आहेत?',
      'हरभरा पिकातील घाटे अळीचे नियंत्रण कसे करावे?'
    ],
    yojanaPrompts: [
      'शेततळे (Farm Pond) अनुदानाची माहिती काय आहे?',
      'पीएम किसान योजनेसाठी कोण पात्र आहे?',
      'जल हौद अनुदानाचे नियम व अटी काय आहेत?',
      'डिग्गी बांधकामासाठी शासकीय अनुदान किती मिळते?'
    ],
    ashaPrompts: [
      'पीएम मातृ वंदना योजनेतून आर्थिक लाभ कसा मिळतो?',
      'गरोदर महिलांसाठी आवश्यक सकस आहार व पोषण सल्ला काय आहे?',
      'जननी सुरक्षा योजनेअंतर्गत शासकीय रुग्णालयात काय लाभ मिळतात?',
      'नवजात बालकांसाठी लसीकरण वेळापत्रक काय आहे?'
    ]
  },
  ta: {
    appTitle: 'ஹக்தார்',
    appSubTitle: 'HAQDAAR',
    tagline: 'கிராமப்புற குடிமக்களுக்கான நம்பகமான பன்மொழி குரல் உதவியாளர்',
    badgeText: 'டிஜிட்டல் பொது சேவை • ICAR மற்றும் அரசுத் தகவல்கள்',
    kisanTab: '🌾 கிசான் சகாயக்',
    kisanSub: 'விவசாயம் & பாசன வழிகாட்டி',
    yojanaTab: '🏛️ யோஜனா சகாயக்',
    yojanaSub: 'அரசு நலத்திட்டம் & மானியம்',
    ashaTab: '🩺 ஆஷா சகாயக்',
    ashaSub: 'தாய்-சேய் ஊட்டச்சத்து & நலத்திட்டம்',
    kisanDesc: 'பயிர் சாகுபடி, விதை அளவு மற்றும் நீர்ப்பாசனத்திற்கான சான்றளிக்கப்பட்ட ICAR வழிகாட்டுதல்',
    yojanaDesc: 'அரசு நலத்திட்ட தகுதிகள், தேவையான ஆவணங்கள் மற்றும் அதிகாரப்பூர்வ மானிய விவரங்கள்',
    ashaDesc: 'தாய்-சேய் ஊட்டச்சத்து, தடுப்பூசி அட்டவணை மற்றும் அரசு சுகாதார நலத்திட்டங்கள்',
    schemesHeading: 'இன்றைய முக்கிய அரசு திட்டங்கள்',
    schemesSub: 'அங்கீகரிக்கப்பட்ட விவரங்கள் • தகவலுக்கு அட்டையைத் தொடவும்',
    viewDetailsBtn: 'முழு விவரம் ➔',
    checkEligibilityBtn: 'தகுதி சரிபார் 📋',
    recentHeading: 'சமீபத்திய கேள்விகள்:',
    clearChatBtn: 'உரையாடலை அழிக்க',
    clearConfirmTitle: 'உரையாடலை அழிக்க விரும்புகிறீர்களா?',
    clearConfirmDesc: 'இது முந்தைய கேள்விகள் மற்றும் பதில்களை நீக்கும்.',
    confirmYes: 'ஆம், அழி',
    confirmNo: 'ரத்து செய்',
    copyBtn: 'நகலெடு 📋',
    copiedBtn: 'நகலெடுக்கப்பட்டது! ✅',
    highContrastLabel: 'உயர் மாறுபாடு',
    textSizeLabel: 'எழுத்து அளவு',
    micStart: 'பேச மைக் பொத்தானை அழுத்தவும்',
    micListening: 'கேட்கிறது... பேசுங்கள்',
    micProcessing: 'செயலாக்குகிறது...',
    micStopHint: 'பேசி முடித்தவுடன் நிறுத்தவும்',
    inputLabel: 'உங்கள் கேள்வி (சரிபார்த்து அனுப்பவும்)',
    inputPlaceholder: 'இங்கு உங்கள் கேள்வியை தட்டச்சு செய்யவும்...',
    sendBtn: 'அனுப்புக ➔',
    speakBtn: 'பதிலைக் கேளுங்கள் 🔊',
    pauseBtn: 'நிறுத்துக ⏹️',
    audioPlaying: 'உதவியாளர் பேசுகிறார்...',
    stopAudioBtn: '⏹️ குரலை நிறுத்துக',
    sourceLabel: 'அங்கீகரிக்கப்பட்ட அரசு ஆதாரம்',
    clearBtn: 'அழிக்க',
    quickHeading: 'பரிந்துரைக்கப்பட்ட கேள்விகள்:',
    welcomeGreeting: 'வணக்கம்! ஹக்தார் உங்களை வரவேற்கிறது.',
    welcomeSub: 'விவசாய ஆலோசனை அல்லது அரசு திட்டங்கள் குறித்து தயங்காமல் குரல் மூலம் கேளுங்கள்.',
    heroVoiceTitle: 'உங்கள் மொழியில் நேரடியாகப் பேசி கேட்கவும்',
    heroVoiceSubtitle: 'மைக் அழுத்தி விவசாயம், அரசு திட்டங்கள் அல்லது சுகாதாரம் குறித்து பேசுங்கள்',
    disclaimer: '⚠️ இந்த தகவல் வழிகாட்டுதலுக்கு மட்டுமே. இறுதி ஒப்புதல் மற்றும் மானியம் அரசு அலுவலர்களால் வழங்கப்படும்.',
    officialDisclaimer: '⚠️ திட்ட தகுதி மற்றும் மானிய விவரங்களை அதிகாரப்பூர்வ அரசு தளத்தில் சரிபார்க்கவும்.',
    healthDisclaimer: '⚠️ இது தாய்-சேய் ஊட்டச்சத்து திட்டங்கள் குறித்த தகவல் மட்டுமே. மருத்துவ சிகிச்சைக்காக அரசு மருத்துவரை அணுகவும்.',
    kvkHelpline: '📞 கிசான் கால் சென்டர்: 1800-180-1551 (கட்டணமில்லா) • அருகிலுள்ள KVK மையத்தை தொடர்பு கொள்ளவும்',
    languageSpeakGuidance: '🎙️ நீங்கள் இந்தி, மராத்தி அல்லது தமிழில் நேரடியாகப் பேசிக் கேட்கலாம்',
    kisanPrompts: [
      'கோதுமை சாகுபடிக்கு சிறந்த DBW ரகங்கள் எவை?',
      'கம்பு சாகுபடிக்கு உகந்த காலம் மற்றும் விதை அளவு என்ன?',
      'கடுகு பயிரில் முதல் பாசனம் எப்போது செய்ய வேண்டும்?',
      'பயறு வகைகளில் பூச்சி தாக்குதலை தடுக்கும் முறைகள் என்ன?'
    ],
    yojanaPrompts: [
      'விவசாய நீர் சேமிப்பு மற்றும் பாசன மானியங்கள் என்ன?',
      'பிஎம் கிசான் திட்டத்தின் தகுதிகள் என்ன?',
      'பண்ணைக் குட்டை மானிய விவரங்கள் என்ன?',
      'டிக்கி நீர் தொட்டி திட்டத்தின் தகுதிகள் என்ன?'
    ],
    ashaPrompts: [
      'பிஎம் மாத்ரு வந்தனா யோஜனா திட்டத்தில் ரூ. 6,000 உதவி பெறுவது எப்படி?',
      'கர்ப்பிணிப் பெண்களுக்கான சத்துணவு ஆலோசனைகள் என்ன?',
      'ஜனனி சுரக்ஷா யோஜனா (JSY) மூலம் அரசு மருத்துவமனையில் கிடைக்கும் பலன்கள் என்ன?',
      'குழந்தைகளுக்கான ஆரம்ப தடுப்பூசி அட்டவணை என்ன?'
    ]
  }
};

export default function App() {
  const [language, setLanguage] = useState('hi');
  const [persona, setPersona] = useState('kisan'); // 'kisan', 'yojana', or 'asha'
  const [fontSizeMode, setFontSizeMode] = useState('normal'); // 'normal', 'medium', 'large'
  const [isHighContrast, setIsHighContrast] = useState(false);
  const [recentQuestions, setRecentQuestions] = useState([]);
  const [isClearModalOpen, setIsClearModalOpen] = useState(false);
  const [copiedMessageId, setCopiedMessageId] = useState(null);

  // Top Slideshow State
  const [currentSlide, setCurrentSlide] = useState(0);
  const [isSlidePaused, setIsSlidePaused] = useState(false);

  // Interactive Eligibility Wizard State
  const [activeWizardScheme, setActiveWizardScheme] = useState(null);
  const [wizardStep, setWizardStep] = useState(0);
  const [wizardAnswers, setWizardAnswers] = useState({});
  const [wizardResult, setWizardResult] = useState(null);

  const [messages, setMessages] = useState([
    {
      id: 1,
      sender: 'assistant',
      text: 'नमस्ते! हकदार में आपका स्वागत है। आप मुझसे फसलों की खेती (ICAR), सरकारी योजनाओं अथवा मातृत्व पोषण सहायता की जानकारी सीधे आवाज़ से पूछ सकते हैं।',
      sources: []
    }
  ]);
  const [typedInput, setTypedInput] = useState('');
  const [interimTranscript, setInterimTranscript] = useState('');
  const [sttState, setSttState] = useState(STT_STATES.IDLE);
  const [errorMessage, setErrorMessage] = useState('');
  const [isAssistantThinking, setIsAssistantThinking] = useState(false);
  const [isPlayingAudio, setIsPlayingAudio] = useState(false);
  const [sessionId] = useState(() => 'sess_' + Math.random().toString(36).substring(2, 9));

  const audioRef = useRef(null);
  const audioAbortRef = useRef(null);
  const messagesEndRef = useRef(null);
  const sttManagerRef = useRef(null);
  const textInputRef = useRef(null);
  const carouselRef = useRef(null);

  const t = UI_STRINGS[language] || UI_STRINGS.hi;

  // Auto-advance Top Slideshow every 4.5 seconds
  useEffect(() => {
    if (isSlidePaused) return;
    const timer = setInterval(() => {
      setCurrentSlide(prev => (prev + 1) % HERO_SLIDES.length);
    }, 4500);
    return () => clearInterval(timer);
  }, [isSlidePaused]);

  const nextSlide = () => {
    setCurrentSlide(prev => (prev + 1) % HERO_SLIDES.length);
  };

  const prevSlide = () => {
    setCurrentSlide(prev => (prev - 1 + HERO_SLIDES.length) % HERO_SLIDES.length);
  };

  // Initialize STT Service
  useEffect(() => {
    sttManagerRef.current = new STTManager({
      apiBaseUrl: API_BASE,
      onStateChange: (state) => {
        setSttState(state);
        if (state === STT_STATES.RECORDING) {
          setErrorMessage('');
        }
      },
      onInterimTranscript: (text) => {
        setInterimTranscript(text);
      },
      onFinalTranscript: (text) => {
        setInterimTranscript('');
        if (text && text.trim()) {
          setTypedInput(prev => {
            const clean = text.trim();
            if (!prev || !prev.trim()) {
              return clean;
            }
            if (prev.endsWith(clean)) {
              return prev;
            }
            return prev + ' ' + clean;
          });
          setTimeout(() => {
            if (textInputRef.current) {
              textInputRef.current.focus();
            }
          }, 100);
        }
      },
      onError: (_code, msg) => {
        setInterimTranscript('');
        setErrorMessage(msg);
      }
    });

    return () => {
      if (sttManagerRef.current) {
        sttManagerRef.current.abort();
      }
    };
  }, []);

  // Auto-scroll messages
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, interimTranscript, isAssistantThinking]);

  // Handle Voice Toggle
  const toggleRecording = () => {
    if (!sttManagerRef.current) return;

    if (sttState === STT_STATES.RECORDING) {
      sttManagerRef.current.stopListening();
    } else {
      setErrorMessage('');
      setInterimTranscript('');
      sttManagerRef.current.startListening(language);
    }
  };

  // Play Spoken Audio
  const playSpeech = (text, lang) => {
    if (audioAbortRef.current) {
      audioAbortRef.current.abort();
    }
    const abortController = new AbortController();
    audioAbortRef.current = abortController;

    if (audioRef.current) {
      audioRef.current.pause();
      audioRef.current.currentTime = 0;
      audioRef.current.removeAttribute('src');
    }
    setIsPlayingAudio(false);

    if (!text || !text.trim()) return;

    let safeSpokenText = text.trim();
    if (safeSpokenText.length > 500) {
      const sentenceEnd = safeSpokenText.slice(0, 480).search(/[।.\n][^।.\n]*$/);
      safeSpokenText = sentenceEnd > 40 ? safeSpokenText.slice(0, sentenceEnd + 1) : safeSpokenText.slice(0, 450) + '...';
    }

    const streamUrl = `${API_BASE}/api/tts/stream`;
    fetch(streamUrl, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text: safeSpokenText, language: lang || language }),
      signal: abortController.signal
    })
      .then(res => {
        if (!res.ok) throw new Error('Audio generation failed');
        return res.blob();
      })
      .then(blob => {
        if (abortController.signal.aborted) return;
        const url = URL.createObjectURL(blob);
        setIsPlayingAudio(true);
        if (audioRef.current) {
          audioRef.current.src = url;
          audioRef.current.play().catch(e => {
            if (e.name !== 'AbortError') console.warn('Audio play prevented:', e);
          });
        }
      })
      .catch(err => {
        if (err.name === 'AbortError') return;
        console.error('Audio playback error:', err);
        setErrorMessage('आवाज़ चलाने में समस्या हुई। कृपया पुनः प्रयास करें।');
        setIsPlayingAudio(false);
      });
  };

  const stopAudio = () => {
    if (audioAbortRef.current) {
      audioAbortRef.current.abort();
      audioAbortRef.current = null;
    }
    if (audioRef.current) {
      audioRef.current.pause();
      audioRef.current.currentTime = 0;
      audioRef.current.removeAttribute('src');
      audioRef.current.load();
    }
    setIsPlayingAudio(false);
  };

  // Copy assistant response
  const copyToClipboard = (text, msgId) => {
    if (navigator?.clipboard?.writeText) {
      navigator.clipboard.writeText(text).then(() => {
        setCopiedMessageId(msgId);
        setTimeout(() => setCopiedMessageId(null), 2000);
      }).catch(() => {
        setErrorMessage('कॉपी करने में त्रुटि हुई');
      });
    }
  };

  // Horizontal Carousel Scrolling
  const scrollCarousel = (direction) => {
    if (carouselRef.current) {
      const scrollOffset = direction === 'left' ? -340 : 340;
      carouselRef.current.scrollBy({ left: scrollOffset, behavior: 'smooth' });
    }
  };

  // Open Eligibility Wizard for a specific scheme
  const openEligibilityWizard = (schemeId) => {
    setActiveWizardScheme(schemeId);
    setWizardStep(0);
    setWizardAnswers({});
    setWizardResult(null);
  };

  // Deterministic rule evaluation mirroring backend/scheme_adapter.py
  const handleWizardAnswer = (questionKey, answerValue) => {
    const updated = { ...wizardAnswers, [questionKey]: answerValue };
    setWizardAnswers(updated);

    if (activeWizardScheme === 'pm_kisan') {
      if (questionKey === 'has_land') {
        if (!answerValue) {
          setWizardResult({
            outcome: 'POTENTIALLY_INELIGIBLE',
            title: 'वर्तमान में अपात्र (Potentially Ineligible)',
            reason: 'पीएम किसान योजना के दिशा-निर्देशों के अनुसार परिवार के नाम राजस्व रिकॉर्ड में कृषि भूमि होना अनिवार्य है।',
            advice: 'भूमिहीन कृषि श्रमिक मनरेगा (MGNREGA) या ई-श्रम पोर्टल के तहत कल्याणकारी योजनाओं का लाभ ले सकते हैं।'
          });
          return;
        }
        setWizardStep(1);
      } else if (questionKey === 'is_taxpayer') {
        if (answerValue) {
          setWizardResult({
            outcome: 'POTENTIALLY_INELIGIBLE',
            title: 'अपात्र (Taxpayer Exclusion)',
            reason: 'बहिष्करण नियम 3.2: पिछले मूल्यांकन वर्ष में आयकर का भुगतान करने वाले व्यक्ति/परिवार अपात्र हैं।',
            advice: 'यदि आपकी आयकर स्थिति में बदलाव हुआ है, तो संबंधित राजस्व अधिकारी से सत्यापन कराएं।'
          });
          return;
        }
        setWizardStep(2);
      } else if (questionKey === 'is_govt_emp') {
        if (answerValue) {
          setWizardResult({
            outcome: 'POTENTIALLY_INELIGIBLE',
            title: 'अपात्र (Govt Employee Exclusion)',
            reason: 'नियम: सेवारत या सेवानिवृत्त सरकारी कर्मचारी (ग्रुप D / MTS को छोड़कर) इस योजना में पात्र नहीं हैं।',
            advice: 'चतुर्थ श्रेणी / ग्रुप D कर्मचारी छूट प्राप्त हैं। अपनी श्रेणी की पुष्टि करें।'
          });
          return;
        }
        setWizardResult({
          outcome: 'POTENTIALLY_ELIGIBLE',
          title: 'संभावित रूप से पात्र (Potentially Eligible)',
          reason: 'आपके पास कृषि भूमि है और कोई बहिष्करण नियम लागू नहीं होता।',
          benefit: '₹6,000 प्रति वर्ष (₹2,000 की 3 समान किस्तों में प्रत्यक्ष बैंक अंतरण DBT)।',
          docs: ['आधार कार्ड व आधार से जुड़ा बैंक खाता', 'जमाबंदी / खतौनी भूमि रिकॉर्ड'],
          advice: 'यह सांकेतिक स्व-मूल्यांकन है। अंतिम सत्यापन pmkisan.gov.in पर पटवारी/तहसीलदार द्वारा किया जाता है।'
        });
      }
    } else if (activeWizardScheme === 'jal_hauz_rajkisan' || activeWizardScheme === 'diggi_rajkisan') {
      if (questionKey === 'in_rajasthan') {
        if (!answerValue) {
          setWizardResult({
            outcome: 'POTENTIALLY_INELIGIBLE',
            title: 'अपात्र (State Boundary)',
            reason: 'यह योजना केवल राजस्थान राज्य के किसानों के लिए राजकिसान साथी पोर्टल पर उपलब्ध है।',
            advice: 'कृपया अपने संबंधित राज्य के कृषि विभाग की सिंचाई योजनाओं की जांच करें।'
          });
          return;
        }
        setWizardStep(1);
      } else if (questionKey === 'has_min_land') {
        if (!answerValue) {
          setWizardResult({
            outcome: 'POTENTIALLY_INELIGIBLE',
            title: 'अपात्र (Minimum Land Requirement)',
            reason: 'डिग्गी एवं पक्का जल हौज निर्माण अनुदान हेतु न्यूनतम 0.5 हेक्टेयर (लगभग 2 बीघा) सिंचित कृषि भूमि अनिवार्य है।',
            advice: 'सामूहिक जल संचयन अथवा अन्य लघु सिंचाई योजनाओं की जानकारी प्राप्त करें।'
          });
          return;
        }
        setWizardResult({
          outcome: 'POTENTIALLY_ELIGIBLE',
          title: 'संभावित रूप से पात्र (Potentially Eligible)',
          reason: 'आप राजस्थान में 0.5 हेक्टेयर से अधिक कृषि भूमि रखते हैं।',
          benefit: 'लागत का 50% से 85% तक अनुदान (पोर्टल विवरण अनुसार)।',
          docs: ['जन आधार कार्ड', 'जमाबंदी नकल (6 माह से पुरानी न हो)', 'नक्शा ट्रेस'],
          advice: 'महत्वपूर्ण शर्त: कृषि विभाग से पूर्व प्रशासनिक स्वीकृति (Administrative Approval) मिलने के बाद ही निर्माण शुरू करें।'
        });
      }
    } else if (activeWizardScheme === 'pmmvy') {
      if (questionKey === 'is_regular_govt') {
        if (answerValue) {
          setWizardResult({
            outcome: 'POTENTIALLY_INELIGIBLE',
            title: 'अपात्र (PMMVY Exclusion)',
            reason: 'नियमित सरकारी या सार्वजनिक उपक्रम में कार्यरत महिला कर्मचारियों को मातृत्व अवकाश लाभ मिलता है, अतः वे PMMVY में शामिल नहीं हैं।',
            advice: 'संबंधित नियोक्ता से मातृत्व हितलाभ अधिनियम के तहत अवकाश व लाभ प्राप्त करें।'
          });
          return;
        }
        setWizardResult({
          outcome: 'POTENTIALLY_ELIGIBLE',
          title: 'संभावित रूप से पात्र (Potentially Eligible)',
          reason: 'गर्भवती व धात्री माताएं (प्रथम शिशु या द्वितीय कन्या शिशु) पोषण सहायता के लिए पात्र हैं।',
          benefit: 'प्रथम शिशु पर ₹5,000 व द्वितीय कन्या शिशु होने पर ₹6,000 डीबीटी सहायता।',
          docs: ['मातृ एवं शिशु सुरक्षा (MCP) कार्ड', 'माता व पिता का आधार कार्ड', 'आधार लिंक बैंक पासबुक'],
          advice: 'निकटतम आंगनवाड़ी केंद्र अथवा आशा कार्यकर्ता से संपर्क कर पंजीकरण कराएं।'
        });
      }
    }
  };

  // Handle Send Message
  const handleSendMessage = async (textToSend) => {
    const query = (textToSend || typedInput).trim();
    if (!query) return;

    stopAudio();

    setRecentQuestions(prev => {
      const filtered = prev.filter(q => q !== query);
      return [query, ...filtered].slice(0, 5);
    });

    const userMsg = {
      id: Date.now(),
      sender: 'user',
      text: query,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    };

    setMessages(prev => [...prev, userMsg]);
    setTypedInput('');
    setInterimTranscript('');
    setIsAssistantThinking(true);
    setErrorMessage('');

    try {
      const response = await fetch(`${API_BASE}/api/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: query,
          language: language,
          persona: persona === 'asha' ? 'yojana' : persona,
          session_id: sessionId
        })
      });

      if (!response.ok) {
        throw new Error(`Server returned ${response.status}`);
      }

      const data = await response.json();
      const assistantMsg = {
        id: Date.now() + 1,
        sender: 'assistant',
        text: data.reply_text,
        spokenText: data.spoken_text || data.reply_text,
        sources: data.sources || [],
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      };

      setMessages(prev => [...prev, assistantMsg]);
      setIsAssistantThinking(false);

      playSpeech(assistantMsg.spokenText, data.language);

    } catch (err) {
      console.error('Chat error:', err);
      setIsAssistantThinking(false);
      setMessages(prev => [
        ...prev,
        {
          id: Date.now() + 1,
          sender: 'assistant',
          text: 'क्षमा करें, सर्वर से संपर्क नहीं हो सका। कृपया अपनी इंटरनेट कनेक्टिविटी जांचें अथवा पुनः प्रयास करें।',
          sources: []
        }
      ]);
      setErrorMessage('सर्वर से उत्तर प्राप्त नहीं हुआ।');
    }
  };

  const currentPrompts = persona === 'kisan' ? t.kisanPrompts : persona === 'asha' ? t.ashaPrompts : t.yojanaPrompts;
  const currentDomainDesc = persona === 'kisan' ? t.kisanDesc : persona === 'asha' ? t.ashaDesc : t.yojanaDesc;

  return (
    <div className={`haqdaar-app font-${fontSizeMode} ${isHighContrast ? 'high-contrast-mode' : ''}`}>
      {/* Hidden Audio Player for Speech Playback */}
      <audio
        ref={audioRef}
        onEnded={() => setIsPlayingAudio(false)}
        onError={() => setIsPlayingAudio(false)}
      />

      {/* Top Banner: Government-Grade Heritage Header */}
      <header className="app-header">
        <div className="header-top-row">
          <div className="brand-group">
            <div className="emblem-wrapper" aria-hidden="true">
              <span className="emblem-flag">🇮🇳</span>
            </div>
            <div className="brand-titles">
              <div className="brand-main">
                <span className="app-name">{t.appTitle}</span>
                <span className="app-subname">{t.appSubTitle}</span>
              </div>
              <p className="app-tagline">{t.tagline}</p>
            </div>
          </div>

          {/* Accessible Large Language Switcher */}
          <div className="lang-selector-group" role="group" aria-label="Select Language">
            {[
              { code: 'hi', label: 'हिन्दी' },
              { code: 'mr', label: 'मराठी' },
              { code: 'ta', label: 'தமிழ்' }
            ].map((l) => (
              <button
                key={l.code}
                type="button"
                className={`lang-pill-btn ${language === l.code ? 'active' : ''}`}
                onClick={() => setLanguage(l.code)}
                aria-pressed={language === l.code}
              >
                {l.label}
              </button>
            ))}
          </div>
        </div>

        {/* Accessibility & Civic Tool Bar */}
        <div className="accessibility-row">
          <div className="text-size-control" role="group" aria-label={t.textSizeLabel}>
            <span className="access-label">{t.textSizeLabel}:</span>
            <button
              type="button"
              className={`size-btn ${fontSizeMode === 'normal' ? 'active' : ''}`}
              onClick={() => setFontSizeMode('normal')}
              title="Normal size"
            >
              अ
            </button>
            <button
              type="button"
              className={`size-btn ${fontSizeMode === 'medium' ? 'active' : ''}`}
              onClick={() => setFontSizeMode('medium')}
              title="Medium size"
            >
              अ+
            </button>
            <button
              type="button"
              className={`size-btn ${fontSizeMode === 'large' ? 'active' : ''}`}
              onClick={() => setFontSizeMode('large')}
              title="Large size"
            >
              अ++
            </button>
          </div>

          <div className="utility-actions">
            <button
              type="button"
              className={`contrast-toggle-btn ${isHighContrast ? 'active' : ''}`}
              onClick={() => setIsHighContrast(!isHighContrast)}
              aria-label={t.highContrastLabel}
            >
              {isHighContrast ? '☀️ सामान्य' : '🌓 ' + t.highContrastLabel}
            </button>
            {messages.length > 1 && (
              <button
                type="button"
                className="clear-chat-btn"
                onClick={() => setIsClearModalOpen(true)}
                title={t.clearChatBtn}
              >
                🗑️ {t.clearChatBtn}
              </button>
            )}
          </div>
        </div>

        {/* Tri-Persona Switcher: Kisan, Yojana, and ASHA Sahayak */}
        <nav className="persona-nav-wrapper tri-persona" aria-label="Assistant Domain">
          <button
            type="button"
            className={`persona-card-btn ${persona === 'kisan' ? 'active' : ''}`}
            onClick={() => setPersona('kisan')}
            aria-pressed={persona === 'kisan'}
          >
            <span className="persona-icon">🌾</span>
            <span className="persona-text-col">
              <strong className="persona-title">{t.kisanTab}</strong>
              <small className="persona-sub">{t.kisanSub}</small>
            </span>
          </button>

          <button
            type="button"
            className={`persona-card-btn ${persona === 'yojana' ? 'active' : ''}`}
            onClick={() => setPersona('yojana')}
            aria-pressed={persona === 'yojana'}
          >
            <span className="persona-icon">🏛️</span>
            <span className="persona-text-col">
              <strong className="persona-title">{t.yojanaTab}</strong>
              <small className="persona-sub">{t.yojanaSub}</small>
            </span>
          </button>

          <button
            type="button"
            className={`persona-card-btn asha-tab ${persona === 'asha' ? 'active' : ''}`}
            onClick={() => setPersona('asha')}
            aria-pressed={persona === 'asha'}
          >
            <span className="persona-icon">🩺</span>
            <span className="persona-text-col">
              <strong className="persona-title">{t.ashaTab}</strong>
              <small className="persona-sub">{t.ashaSub}</small>
            </span>
          </button>
        </nav>

        {/* Dynamic Context Banner */}
        <div className="domain-scope-banner">
          <span className="scope-icon">{persona === 'asha' ? '🩺' : 'ℹ️'}</span>
          <span className="scope-desc">{currentDomainDesc}</span>
        </div>
      </header>

      {/* Top Interactive Government Schemes Showcase Slideshow Banner */}
      <section
        className="top-schemes-slideshow"
        aria-label="Government Schemes Showcase"
        onMouseEnter={() => setIsSlidePaused(true)}
        onMouseLeave={() => setIsSlidePaused(false)}
      >
        <div className="slides-track-wrapper">
          {HERO_SLIDES.map((slide, sIdx) => (
            <div
              key={slide.id}
              className={`slide-item ${sIdx === currentSlide ? 'active' : ''}`}
              aria-hidden={sIdx !== currentSlide}
            >
              <img
                src={slide.image}
                alt={slide.title[language] || slide.title.hi}
                className="slide-image"
              />
              <div className="slide-gradient-overlay" />
              <div className="slide-content-overlay">
                <span className="slide-tag-pill">
                  {slide.tag[language] || slide.tag.hi}
                </span>
                <h2 className="slide-headline">
                  {slide.title[language] || slide.title.hi}
                </h2>
                <p className="slide-subtext">
                  {slide.subtitle[language] || slide.subtitle.hi}
                </p>
                <div className="slide-action-row">
                  <button
                    type="button"
                    className="slide-query-btn"
                    onClick={() => handleSendMessage(slide.query[language] || slide.query.hi)}
                  >
                    <span>{slide.askBtnText[language] || slide.askBtnText.hi}</span>
                    <span className="btn-arrow">➔</span>
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Manual Arrow Controls */}
        <button
          type="button"
          className="slide-nav-arrow prev"
          onClick={prevSlide}
          aria-label="Previous Slide"
        >
          ❮
        </button>
        <button
          type="button"
          className="slide-nav-arrow next"
          onClick={nextSlide}
          aria-label="Next Slide"
        >
          ❯
        </button>

        {/* Indicator Dots */}
        <div className="slide-indicators-bar" role="tablist">
          {HERO_SLIDES.map((_, dotIdx) => (
            <button
              key={dotIdx}
              type="button"
              className={`slide-dot-btn ${dotIdx === currentSlide ? 'active' : ''}`}
              onClick={() => setCurrentSlide(dotIdx)}
              aria-label={`Go to slide ${dotIdx + 1}`}
            />
          ))}
        </div>
      </section>

      {/* Main 2-Column Responsive Dashboard Body */}
      <div className="dashboard-layout-container">
        {/* Left Sidebar: Schemes & Citizen Discovery Deck */}
        <aside className="dashboard-sidebar" aria-label="Schemes and Citizen Tools">
          {/* Government Schemes Carousel Section */}
          <section className="schemes-carousel-section" aria-label={t.schemesHeading}>
            <div className="schemes-section-header">
              <div className="schemes-title-group">
                <h2 className="schemes-main-heading">🏛️ {t.schemesHeading}</h2>
                <p className="schemes-sub-heading">{t.schemesSub}</p>
              </div>
              <div className="carousel-nav-arrows" aria-hidden="true">
                <button
                  type="button"
                  className="carousel-arrow-btn"
                  onClick={() => scrollCarousel('left')}
                  aria-label="Previous schemes"
                >
                  ◀
                </button>
                <button
                  type="button"
                  className="carousel-arrow-btn"
                  onClick={() => scrollCarousel('right')}
                  aria-label="Next schemes"
                >
                  ▶
                </button>
              </div>
            </div>

            <div className="schemes-cards-carousel" ref={carouselRef} tabIndex="0" role="region" aria-label="Schemes Carousel">
              {VERIFIED_SCHEMES.map((scheme) => (
                <article key={scheme.id} className="scheme-card">
                  <div className="scheme-card-top">
                    <span className="scheme-icon-badge">{scheme.icon}</span>
                    <span className="scheme-category-tag">{scheme.category[language] || scheme.category.hi}</span>
                  </div>

                  <h3 className="scheme-card-title">{scheme.name[language] || scheme.name.hi}</h3>

                  <div className="scheme-card-details">
                    <div className="scheme-detail-row">
                      <strong className="scheme-row-label">वित्तीय लाभ / Benefit:</strong>
                      <p className="scheme-row-value">{scheme.benefit[language] || scheme.benefit.hi}</p>
                    </div>
                    <div className="scheme-detail-row">
                      <strong className="scheme-row-label">पात्रता / Eligibility:</strong>
                      <p className="scheme-row-value">{scheme.eligibility[language] || scheme.eligibility.hi}</p>
                    </div>
                  </div>

                  <div className="scheme-card-footer">
                    <button
                      type="button"
                      className="scheme-eligibility-btn"
                      onClick={() => openEligibilityWizard(scheme.id)}
                    >
                      {t.checkEligibilityBtn}
                    </button>
                    <button
                      type="button"
                      className="scheme-action-btn"
                      onClick={() => handleSendMessage(scheme.query[language] || scheme.query.hi)}
                    >
                      {t.viewDetailsBtn}
                    </button>
                  </div>
                </article>
              ))}
            </div>
            <p className="schemes-carousel-disclaimer">{t.officialDisclaimer}</p>
          </section>

          {/* Persona-Aware Quick Suggested Questions */}
          <section className="sidebar-quick-section" aria-label="Suggested Questions">
            <h3 className="sidebar-section-title">💡 {t.quickHeading}</h3>
            <div className="sidebar-prompts-list">
              {currentPrompts.map((prompt, idx) => (
                <button
                  key={idx}
                  type="button"
                  className="sidebar-prompt-card"
                  onClick={() => handleSendMessage(prompt)}
                >
                  <span className="prompt-bullet">➔</span>
                  <span className="prompt-text">{prompt}</span>
                </button>
              ))}
            </div>
          </section>

          {/* Recent Queries Strip (When Available) */}
          {recentQuestions.length > 0 && (
            <section className="recent-questions-box" aria-label={t.recentHeading}>
              <span className="recent-strip-label">🕒 {t.recentHeading}</span>
              <div className="recent-chips-list">
                {recentQuestions.map((q, idx) => (
                  <button
                    key={idx}
                    type="button"
                    className="recent-chip-btn"
                    onClick={() => handleSendMessage(q)}
                  >
                    {q}
                  </button>
                ))}
              </div>
            </section>
          )}

          {/* Civic Helpline Banner */}
          <aside className="civic-helpline-banner" aria-label="Official Helpline">
            <span className="helpline-icon">📞</span>
            <span className="helpline-text">{t.kvkHelpline}</span>
          </aside>
        </aside>

        {/* Right Main Studio: Voice & Conversation Area */}
        <main className="dashboard-main-studio">
          {/* Hero Voice Studio (Front-and-Center Focal Point) */}
          <section className="hero-voice-studio-card" aria-label="Voice Interaction Studio">
            <div className="hero-voice-header">
              <span className="voice-status-badge">
                <span className="pulsing-record-dot"></span>
                <span>{t.languageSpeakGuidance}</span>
              </span>
              <h2 className="hero-voice-heading">{t.heroVoiceTitle}</h2>
              <p className="hero-voice-sub">{t.heroVoiceSubtitle}</p>
            </div>

            {/* Giant Central Microphone Button */}
            <div className="central-mic-container">
              <button
                type="button"
                className={`central-hero-mic ${sttState === STT_STATES.RECORDING ? 'is-recording' : ''}`}
                onClick={toggleRecording}
                aria-label={sttState === STT_STATES.RECORDING ? 'Stop Recording' : 'Start Voice Recording'}
              >
                {sttState === STT_STATES.RECORDING ? (
                  <div className="mic-stop-square" aria-hidden="true" />
                ) : (
                  <span className="central-mic-glyph" aria-hidden="true">🎤</span>
                )}
              </button>
              <span className="central-mic-caption">
                {sttState === STT_STATES.RECORDING
                  ? t.micListening
                  : sttState === STT_STATES.PROCESSING
                    ? t.micProcessing
                    : t.micStart}
              </span>
            </div>

            {/* Live Sound Bars Animation when Recording */}
            {sttState === STT_STATES.RECORDING && (
              <div className="live-speech-waves" aria-label="Listening to your voice">
                <i></i><i></i><i></i><i></i><i></i>
              </div>
            )}

            {/* Real-time Interim Live Voice Feedback */}
            {interimTranscript && (
              <div className="interim-preview-card" aria-live="assertive">
                <div className="interim-header">
                  <span className="listening-dot"></span>
                  <span>सुन रहा हूँ (Live)...</span>
                </div>
                <p className="interim-text">{interimTranscript}</p>
              </div>
            )}

            {/* Prominent Transcript Review & Edit Box (Appears when voice captures speech) */}
            {typedInput && (
              <div className="central-review-card" role="region" aria-label="Review Voice Transcript">
                <div className="central-review-top">
                  <strong className="review-label">✏️ {t.inputLabel}</strong>
                  <button
                    type="button"
                    className="review-clear-action"
                    onClick={() => setTypedInput('')}
                  >
                    🗑️ {t.clearBtn}
                  </button>
                </div>
                <textarea
                  ref={textInputRef}
                  className="central-review-textarea"
                  value={typedInput}
                  onChange={(e) => setTypedInput(e.target.value)}
                  placeholder={t.inputPlaceholder}
                  rows={2}
                />
                <div className="central-review-bottom">
                  <span className="review-tip-text">माइक से बोला गया सवाल जांचें। सही हो तो 'पूछें' दबाएं:</span>
                  <button
                    type="button"
                    className="central-send-button"
                    onClick={() => handleSendMessage()}
                    disabled={!typedInput.trim() || isAssistantThinking}
                  >
                    {t.sendBtn}
                  </button>
                </div>
              </div>
            )}
          </section>

          {/* Health Disclaimer when in ASHA Persona */}
          {persona === 'asha' && (
            <div className="asha-notice-banner" role="note">
              <span>🩺 {t.healthDisclaimer}</span>
            </div>
          )}

          {/* Message Feed Canvas */}
          <div className="messages-feed" role="log" aria-live="polite">
            {messages.map((msg) => (
              <article
                key={msg.id}
                className={`message-card-wrapper ${msg.sender}`}
              >
                <div className="message-card">
                  {/* Message Header Badge */}
                  <div className="message-header-meta">
                    <span className="sender-indicator">
                      {msg.sender === 'assistant'
                        ? (persona === 'asha' ? '🩺 आशा सलाहकार' : '🏛️ हकदार सहायक')
                        : '👤 आपका सवाल'}
                    </span>
                    <time className="message-time">{msg.timestamp}</time>
                  </div>

                  {/* Message Text with Structured Formatting */}
                  <div className="message-body-text">
                    {msg.text.split('\n\n').map((paragraph, pIdx) => {
                      const lines = paragraph.split('\n');
                      const hasBullets = lines.some(l => l.trim().startsWith('•') || l.trim().startsWith('-'));
                      if (hasBullets) {
                        return (
                          <div key={pIdx} className="message-bullet-group">
                            {lines.map((line, lIdx) => (
                              <p key={lIdx} className="message-paragraph message-bullet-item">
                                {line}
                              </p>
                            ))}
                          </div>
                        );
                      }
                      return (
                        <p key={pIdx} className="message-paragraph">{paragraph}</p>
                      );
                    })}
                  </div>

                  {/* Verified Official Sources (Shown ONLY when backend provides them) */}
                  {msg.sources && msg.sources.length > 0 && (
                    <footer className="sources-citation-box">
                      <span className="sources-heading">📌 {t.sourceLabel}:</span>
                      <ul className="sources-list">
                        {msg.sources.map((s, sIdx) => (
                          <li key={sIdx} className="source-pill">
                            <strong className="source-doc-title">{s.title || 'अभिलेख'}</strong>
                            {s.institution && (
                              <span className="source-inst"> — {s.institution}</span>
                            )}
                            {s.year && (
                              <span className="source-year"> ({s.year})</span>
                            )}
                          </li>
                        ))}
                      </ul>
                    </footer>
                  )}

                  {/* Assistant Card Action Controls (Voice Playback & Copy) */}
                  {msg.sender === 'assistant' && (
                    <div className="assistant-card-actions">
                      <button
                        type="button"
                        className="speech-action-btn"
                        onClick={() => playSpeech(msg.spokenText || msg.text, language)}
                      >
                        {t.speakBtn}
                      </button>
                      {isPlayingAudio && (
                        <button
                          type="button"
                          className="speech-action-btn stop"
                          onClick={stopAudio}
                        >
                          {t.pauseBtn}
                        </button>
                      )}
                      <button
                        type="button"
                        className="speech-action-btn copy-btn"
                        onClick={() => copyToClipboard(msg.text, msg.id)}
                      >
                        {copiedMessageId === msg.id ? t.copiedBtn : t.copyBtn}
                      </button>
                    </div>
                  )}
                </div>
              </article>
            ))}

            {/* Thinking State Indicator */}
            {isAssistantThinking && (
              <div className="thinking-card" aria-label="Processing Response">
                <div className="pulsing-wave-dots">
                  <span></span>
                  <span></span>
                  <span></span>
                </div>
                <span className="thinking-status-text">
                  सत्यापित संदर्भ में प्रामाणिक जानकारी खोजी जा रही है...
                </span>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>

          {/* Bottom Chat Composer with Voice Mic, Text Input & Send */}
          <footer className="interaction-studio">
            <form
              className="chat-submit-form"
              onSubmit={(e) => {
                e.preventDefault();
                handleSendMessage();
              }}
            >
              <button
                type="button"
                className={`composer-mic-btn ${sttState === STT_STATES.RECORDING ? 'is-recording' : ''}`}
                onClick={toggleRecording}
                aria-label={sttState === STT_STATES.RECORDING ? 'माइक बंद करें / Stop Recording' : 'माइक से बोलें / Voice Input'}
                title={sttState === STT_STATES.RECORDING ? t.micListening : t.micStart}
              >
                {sttState === STT_STATES.RECORDING ? (
                  <span className="composer-mic-stop-sq" aria-hidden="true" />
                ) : (
                  <span className="composer-mic-glyph" aria-hidden="true">🎤</span>
                )}
              </button>
              <input
                ref={textInputRef}
                type="text"
                className="chat-text-field"
                value={typedInput}
                onChange={(e) => setTypedInput(e.target.value)}
                placeholder={sttState === STT_STATES.RECORDING ? t.micListening : t.inputPlaceholder}
                aria-label="Ask Question"
              />
              <button
                type="submit"
                className="chat-submit-btn"
                disabled={!typedInput.trim() || isAssistantThinking}
                aria-label="Send Query"
              >
                {t.sendBtn}
              </button>
            </form>
            <p className="statutory-disclaimer">{t.disclaimer}</p>
          </footer>
        </main>
      </div>

      {/* Interactive Eligibility Wizard Modal (Based on backend/scheme_adapter.py) */}
      {activeWizardScheme && (
        <div className="modal-backdrop" role="dialog" aria-modal="true">
          <div className="wizard-modal-card">
            <div className="wizard-modal-header">
              <h3 className="wizard-title">📋 योजना पात्रता स्व-मूल्यांकन</h3>
              <button
                type="button"
                className="wizard-close-btn"
                onClick={() => setActiveWizardScheme(null)}
              >
                ✕
              </button>
            </div>

            {/* PM-KISAN Evaluation Steps */}
            {activeWizardScheme === 'pm_kisan' && !wizardResult && (
              <div className="wizard-step-body">
                <span className="wizard-scheme-tag">💰 पीएम किसान सम्मान निधि</span>
                {wizardStep === 0 && (
                  <div className="wizard-question-box">
                    <p className="wizard-question-text">प्रश्न 1: क्या आपके परिवार के नाम राजस्व रिकॉर्ड में कृषि योग्य भूमि दर्ज है?</p>
                    <div className="wizard-options-row">
                      <button
                        type="button"
                        className="wizard-opt-btn primary"
                        onClick={() => handleWizardAnswer('has_land', true)}
                      >
                        हाँ, भूमि दर्ज है
                      </button>
                      <button
                        type="button"
                        className="wizard-opt-btn"
                        onClick={() => handleWizardAnswer('has_land', false)}
                      >
                        नहीं, भूमि नहीं है
                      </button>
                    </div>
                  </div>
                )}
                {wizardStep === 1 && (
                  <div className="wizard-question-box">
                    <p className="wizard-question-text">प्रश्न 2: क्या परिवार के किसी सदस्य ने पिछले वित्तीय वर्ष में आयकर (Income Tax) का भुगतान किया है?</p>
                    <div className="wizard-options-row">
                      <button
                        type="button"
                        className="wizard-opt-btn"
                        onClick={() => handleWizardAnswer('is_taxpayer', true)}
                      >
                        हाँ, टैक्स भरा है
                      </button>
                      <button
                        type="button"
                        className="wizard-opt-btn primary"
                        onClick={() => handleWizardAnswer('is_taxpayer', false)}
                      >
                        नहीं, टैक्स नहीं भरते
                      </button>
                    </div>
                  </div>
                )}
                {wizardStep === 2 && (
                  <div className="wizard-question-box">
                    <p className="wizard-question-text">प्रश्न 3: क्या कोई सदस्य नियमित सरकारी सेवा में कार्यरत या पेंशनभोगी है (ग्रुप D / MTS को छोड़कर)?</p>
                    <div className="wizard-options-row">
                      <button
                        type="button"
                        className="wizard-opt-btn"
                        onClick={() => handleWizardAnswer('is_govt_emp', true)}
                      >
                        हाँ, सरकारी कर्मचारी हैं
                      </button>
                      <button
                        type="button"
                        className="wizard-opt-btn primary"
                        onClick={() => handleWizardAnswer('is_govt_emp', false)}
                      >
                        नहीं / केवल ग्रुप D कर्मचारी
                      </button>
                    </div>
                  </div>
                )}
              </div>
            )}

            {/* Diggi / Jal Hauz Evaluation Steps */}
            {(activeWizardScheme === 'jal_hauz_rajkisan' || activeWizardScheme === 'diggi_rajkisan') && !wizardResult && (
              <div className="wizard-step-body">
                <span className="wizard-scheme-tag">💧 जल संचयन व डिग्गी अनुदान</span>
                {wizardStep === 0 && (
                  <div className="wizard-question-box">
                    <p className="wizard-question-text">प्रश्न 1: क्या आपकी कृषि भूमि राजस्थान राज्य में स्थित है?</p>
                    <div className="wizard-options-row">
                      <button
                        type="button"
                        className="wizard-opt-btn primary"
                        onClick={() => handleWizardAnswer('in_rajasthan', true)}
                      >
                        हाँ, राजस्थान में है
                      </button>
                      <button
                        type="button"
                        className="wizard-opt-btn"
                        onClick={() => handleWizardAnswer('in_rajasthan', false)}
                      >
                        नहीं, अन्य राज्य में है
                      </button>
                    </div>
                  </div>
                )}
                {wizardStep === 1 && (
                  <div className="wizard-question-box">
                    <p className="wizard-question-text">प्रश्न 2: क्या आपके पास न्यूनतम 0.5 हेक्टेयर (लगभग 2 बीघा) सिंचित कृषि भूमि है?</p>
                    <div className="wizard-options-row">
                      <button
                        type="button"
                        className="wizard-opt-btn primary"
                        onClick={() => handleWizardAnswer('has_min_land', true)}
                      >
                        हाँ, 0.5 हेक्टेयर या अधिक
                      </button>
                      <button
                        type="button"
                        className="wizard-opt-btn"
                        onClick={() => handleWizardAnswer('has_min_land', false)}
                      >
                        नहीं, 0.5 हेक्टेयर से कम
                      </button>
                    </div>
                  </div>
                )}
              </div>
            )}

            {/* PMMVY Maternity Evaluation Steps */}
            {activeWizardScheme === 'pmmvy' && !wizardResult && (
              <div className="wizard-step-body">
                <span className="wizard-scheme-tag">🤱 पीएम मातृ वंदना योजना</span>
                <div className="wizard-question-box">
                  <p className="wizard-question-text">क्या गर्भवती/धात्री माता किसी नियमित सरकारी सेवा अथवा सार्वजनिक उपक्रम (PSU) में कार्यरत हैं?</p>
                  <div className="wizard-options-row">
                    <button
                      type="button"
                      className="wizard-opt-btn"
                      onClick={() => handleWizardAnswer('is_regular_govt', true)}
                    >
                      हाँ, सरकारी कर्मचारी हैं
                    </button>
                    <button
                      type="button"
                      className="wizard-opt-btn primary"
                      onClick={() => handleWizardAnswer('is_regular_govt', false)}
                    >
                      नहीं, निजी / गृहिणी / श्रमिक
                    </button>
                  </div>
                </div>
              </div>
            )}

            {/* Result View */}
            {wizardResult && (
              <div className={`wizard-result-card ${wizardResult.outcome}`}>
                <div className="wizard-result-badge">
                  {wizardResult.outcome === 'POTENTIALLY_ELIGIBLE' ? '🟢' : '🔴'} {wizardResult.title}
                </div>
                <p className="wizard-result-reason">{wizardResult.reason}</p>
                {wizardResult.benefit && (
                  <p className="wizard-result-benefit"><strong>लाभ:</strong> {wizardResult.benefit}</p>
                )}
                {wizardResult.docs && (
                  <div className="wizard-result-docs">
                    <strong>आवश्यक दस्तावेज:</strong>
                    <ul>
                      {wizardResult.docs.map((d, i) => <li key={i}>{d}</li>)}
                    </ul>
                  </div>
                )}
                <p className="wizard-result-advice">ℹ️ {wizardResult.advice}</p>
                <div className="wizard-result-actions">
                  <button
                    type="button"
                    className="wizard-ask-btn"
                    onClick={() => {
                      const schemeObj = VERIFIED_SCHEMES.find(s => s.id === activeWizardScheme);
                      if (schemeObj) {
                        handleSendMessage(schemeObj.query[language] || schemeObj.query.hi);
                      }
                      setActiveWizardScheme(null);
                    }}
                  >
                    सहायक से पूरी जानकारी पूछें ➔
                  </button>
                  <button
                    type="button"
                    className="wizard-reset-btn"
                    onClick={() => {
                      setWizardStep(0);
                      setWizardAnswers({});
                      setWizardResult(null);
                    }}
                  >
                    पुनः जांचें
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Floating Error Toast */}
      {errorMessage && (
        <div className="alert-toast-bar" role="alert">
          <span className="alert-icon">⚠️</span>
          <span className="alert-text">{errorMessage}</span>
          <button
            type="button"
            className="alert-dismiss-btn"
            onClick={() => setErrorMessage('')}
          >
            ✕
          </button>
        </div>
      )}

      {/* Clear Chat Confirmation Modal */}
      {isClearModalOpen && (
        <div className="modal-backdrop" role="dialog" aria-modal="true">
          <div className="modal-card">
            <h3 className="modal-title">⚠️ {t.clearConfirmTitle}</h3>
            <p className="modal-desc">{t.clearConfirmDesc}</p>
            <div className="modal-actions">
              <button
                type="button"
                className="modal-btn-confirm"
                onClick={() => {
                  setMessages([
                    {
                      id: Date.now(),
                      sender: 'assistant',
                      text: t.welcomeGreeting,
                      sources: []
                    }
                  ]);
                  stopAudio();
                  setIsClearModalOpen(false);
                }}
              >
                {t.confirmYes}
              </button>
              <button
                type="button"
                className="modal-btn-cancel"
                onClick={() => setIsClearModalOpen(false)}
              >
                {t.confirmNo}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Immediate Sticky Audio Stop Bar */}
      {isPlayingAudio && (
        <aside className="global-audio-deck" aria-label="Audio Controls">
          <div className="audio-meta">
            <span className="sound-bars-anim">
              <i></i><i></i><i></i>
            </span>
            <span className="audio-label">{t.audioPlaying}</span>
          </div>
          <button
            type="button"
            className="stop-speaking-pill"
            onClick={stopAudio}
            aria-label="Stop Speaking Audio"
          >
            {t.stopAudioBtn}
          </button>
        </aside>
      )}

    </div>
  );
}
