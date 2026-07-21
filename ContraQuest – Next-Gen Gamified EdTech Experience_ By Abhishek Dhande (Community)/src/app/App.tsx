import { useState } from 'react';
import { motion } from 'motion/react';
import { StatusBar } from './components/StatusBar';
import { Header } from './components/Header';
import { ProgressCard } from './components/ProgressCard';
import { DailyStreak } from './components/DailyStreak';
import { CalendarWidget } from './components/CalendarWidget';
import { SubjectsSection } from './components/SubjectsSection';
import { BottomNavigation } from './components/BottomNavigation';
import { QuizScreen } from './components/QuizScreen';
import { GameMapQuizScreen } from './components/GameMapQuizScreen';
import { QuizCompletionScreen } from './components/QuizCompletionScreen';
import { AITutorScreen } from './components/AITutorScreen';
import { LeaderboardScreen } from './components/LeaderboardScreen';
import { ProfileScreen } from './components/ProfileScreen';
import { SubjectDetailScreen } from './components/SubjectDetailScreen';
import { VideosScreen } from './components/VideosScreen';
import { LessonPlayerScreen } from './components/LessonPlayerScreen';
import { ProgressNotification } from './components/ProgressNotification';
import { InlineXPNotification } from './components/InlineXPNotification';
import { ProgressManager, UserProgress, ProgressUtils } from './components/ProgressManager';
import { ProgressSaveIndicator, useSaveStatus } from './components/ProgressSaveIndicator';
import { AmbientParticles } from './components/AmbientParticles';
import { DynamicBackground } from './components/DynamicBackground';
import { OpeningAnimation } from './components/OpeningAnimation';
import { SignupScreen } from './components/SignupScreen';
import { WelcomeScreen } from './components/WelcomeScreen';
import ExportPage from './ExportPage';
import profileImage from 'figma:asset/1627f3a870e9b56d751d07f53392d7a84aa55817.png';


export type Screen = 'opening' | 'signup' | 'welcome' | 'home' | 'quiz' | 'game-map-quiz' | 'quiz-completion' | 'ai' | 'leaderboard' | 'profile' | 'subject-detail' | 'videos' | 'lesson-player';

export interface Subject {
  id: string;
  name: string;
  description: string;
  progress: number;
  icon: React.ReactNode;
  color: string;
}

export default function App() {
  // Export Route - Check first before any other logic
  if (window.location.pathname === '/export') {
    return <ExportPage />;
  }

  // Mobile-first design with touch-optimized interactions
  const [currentScreen, setCurrentScreen] = useState<Screen>('opening');
  const [navigationStack, setNavigationStack] = useState<Screen[]>(['opening']);
  const [selectedSubject, setSelectedSubject] = useState<Subject | null>(null);
  const [selectedLesson, setSelectedLesson] = useState<string | null>(null);
  const [userXP, setUserXP] = useState(5500);
  const [streakCount, setStreakCount] = useState(3);
  const [completionData, setCompletionData] = useState({
    xpGained: 0,
    completionTime: '0:00',
    accuracy: 0,
    totalQuestions: 0,
    correctAnswers: 0,
    stageName: ''
  });
  const [currentProgress, setCurrentProgress] = useState(40);
  const [totalQuizzesCompleted, setTotalQuizzesCompleted] = useState(2);
  const [showXPAnimation, setShowXPAnimation] = useState(false);
  const [recentXPGain, setRecentXPGain] = useState(0);
  const [showProgressNotification, setShowProgressNotification] = useState(false);
  const [notificationData, setNotificationData] = useState({
    type: 'xp-gain' as const,
    title: '',
    subtitle: '',
    xpGain: 0
  });
  const [showInlineXP, setShowInlineXP] = useState(false);
  const [levelProgress, setLevelProgress] = useState(ProgressUtils.calculateLevel(5500));
  const [completedStages, setCompletedStages] = useState<number[]>([]);
  const [achievements, setAchievements] = useState<any[]>([]);
  
  // Save status management
  const { saveStatus, showIndicator, triggerSave, triggerError } = useSaveStatus();

  const illustrationImage = "https://images.unsplash.com/photo-1743247299142-8f1c919776c4?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHwzZCUyMGNoYXJhY3RlciUyMGxlYXJuaW5nJTIwaWxsdXN0cmF0aW9ufGVufDF8fHx8MTc1NzQzMTU5MHww&ixlib=rb-4.1.0&q=80&w=1080&utm_source=figma&utm_medium=referral";

  // Navigation helper functions
  const navigateToScreen = (screen: Screen) => {
    setNavigationStack(prev => [...prev, screen]);
    setCurrentScreen(screen);
  };

  const navigateBack = () => {
    setNavigationStack(prev => {
      if (prev.length > 1) {
        const newStack = [...prev];
        newStack.pop(); // Remove current screen
        const previousScreen = newStack[newStack.length - 1];
        setCurrentScreen(previousScreen);
        
        // Clean up state when going back
        if (previousScreen === 'home') {
          setSelectedSubject(null);
          setSelectedLesson(null);
        }
        
        return newStack;
      }
      return prev;
    });
  };

  const handleSubjectClick = (subject: Subject) => {
    setSelectedSubject(subject);
    navigateToScreen('subject-detail');
  };

  const handleBackToHome = () => {
    setCurrentScreen('home');
    setNavigationStack(['home']);
    setSelectedSubject(null);
    setSelectedLesson(null);
  };

  const handleXPGain = (points: number) => {
    const oldXP = userXP;
    const newXP = oldXP + points;
    
    setRecentXPGain(points);
    setShowXPAnimation(true);
    setUserXP(newXP);
    
    // Update level progress
    const newLevelProgress = ProgressUtils.calculateLevel(newXP);
    setLevelProgress(newLevelProgress);
    
    // Check for level up
    const leveledUp = ProgressUtils.checkForLevelUp(oldXP, newXP);
    if (leveledUp) {
      setNotificationData({
        type: 'level-up',
        title: `Level ${newLevelProgress.currentLevel}!`,
        subtitle: 'You leveled up! Keep going!',
        xpGain: points
      });
      setShowProgressNotification(true);
    } else {
      // Show immediate inline XP feedback
      setShowInlineXP(true);
      setTimeout(() => setShowInlineXP(false), 2000);
      
      // Show detailed XP gain notification for larger amounts
      if (points >= 25) {
        setNotificationData({
          type: 'xp-gain',
          title: 'Excellent Work!',
          subtitle: 'You earned bonus XP!',
          xpGain: points
        });
        setShowProgressNotification(true);
      }
    }
    
    // Trigger save indicator
    triggerProgressSave();
  };

  const handleStreakIncrease = () => {
    setStreakCount(prev => prev + 1);
    
    // Show streak notification
    setNotificationData({
      type: 'streak',
      title: 'Streak Extended!',
      subtitle: `${streakCount + 1} days in a row!`,
      xpGain: 0
    });
    setShowProgressNotification(true);
    
    // Trigger save indicator
    triggerProgressSave();
  };

  const handleLessonClick = (lessonTitle: string) => {
    setSelectedLesson(lessonTitle);
    navigateToScreen('lesson-player');
  };

  const handleQuizCompletion = (data: {
    xpGained: number;
    completionTime: string;
    accuracy: number;
    totalQuestions: number;
    correctAnswers: number;
    stageName: string;
  }) => {
    setCompletionData(data);
    
    // Update progress and stats
    setTotalQuizzesCompleted(prev => prev + 1);
    const newProgress = Math.min(100, currentProgress + (data.accuracy >= 50 ? 20 : 10));
    setCurrentProgress(newProgress);
    
    // Real-time XP gain
    const oldXP = userXP;
    const newXP = oldXP + data.xpGained;
    setRecentXPGain(data.xpGained);
    setShowXPAnimation(true);
    setUserXP(newXP);
    
    // Update level progress
    const newLevelProgress = ProgressUtils.calculateLevel(newXP);
    setLevelProgress(newLevelProgress);
    
    // Check for level up
    const leveledUp = ProgressUtils.checkForLevelUp(oldXP, newXP);
    
    // Show completion notification
    setTimeout(() => {
      if (leveledUp) {
        setNotificationData({
          type: 'level-up',
          title: `Level ${newLevelProgress.currentLevel}!`,
          subtitle: 'Quiz completed with a level up!',
          xpGain: data.xpGained
        });
      } else {
        setNotificationData({
          type: 'quiz-complete',
          title: 'Quiz Completed!',
          subtitle: `${data.correctAnswers}/${data.totalQuestions} correct • ${data.accuracy}% accuracy`,
          xpGain: data.xpGained
        });
      }
      setShowProgressNotification(true);
    }, 1000);
    
    // Trigger save indicator
    triggerProgressSave();
    
    navigateToScreen('quiz-completion');
  };

  const handleXPAnimationComplete = () => {
    setShowXPAnimation(false);
    setRecentXPGain(0);
  };

  const handleNotificationComplete = () => {
    setShowProgressNotification(false);
  };

  // Handle progress loading from storage
  const handleProgressLoaded = (progress: UserProgress) => {
    setUserXP(progress.userXP);
    setStreakCount(progress.streakCount);
    setCurrentProgress(progress.currentProgress);
    setTotalQuizzesCompleted(progress.totalQuizzesCompleted);
    setLevelProgress(progress.levelProgress);
    setCompletedStages(progress.completedStages);
    setAchievements(progress.achievements);
    console.log('📊 Progress loaded:', progress);
  };

  // Trigger save indicator when progress changes
  const triggerProgressSave = () => {
    triggerSave();
  };

  const handleRetakeQuiz = () => {
    navigateToScreen('game-map-quiz');
  };

  const handleNextChallenge = () => {
    setCurrentScreen('home');
    setNavigationStack(['home']);
    setSelectedSubject(null);
    setSelectedLesson(null);
  };

  const handleOpeningComplete = () => {
    navigateToScreen('signup');
  };

  const handleSignupComplete = () => {
    navigateToScreen('welcome');
  };

  const handleWelcomeComplete = () => {
    setCurrentScreen('home');
    setNavigationStack(['home']);
  };

  const renderScreen = () => {
    switch (currentScreen) {
      case 'opening':
        return <OpeningAnimation onAnimationComplete={handleOpeningComplete} />;
      case 'signup':
        return <SignupScreen onBack={navigateBack} onSignupComplete={handleSignupComplete} />;
      case 'welcome':
        return <WelcomeScreen onComplete={handleWelcomeComplete} />;
      case 'home':
        return (
          <div className="space-y-6">
            <Header 
              profileImage={profileImage} 
              userXP={userXP}
              recentXPGain={recentXPGain}
              showXPAnimation={showXPAnimation}
              onXPAnimationComplete={handleXPAnimationComplete}
              levelProgress={levelProgress}
            />
            <div className="px-6">
              <ProgressCard 
                illustrationImage={illustrationImage} 
                onStartQuiz={() => navigateToScreen('game-map-quiz')}
                currentProgress={currentProgress}
                totalQuizzesCompleted={totalQuizzesCompleted}
              />
            </div>
            <div className="px-6">
              <DailyStreak streakCount={streakCount} />
            </div>
            <div className="px-6">
              <CalendarWidget />
            </div>
            <SubjectsSection onSubjectClick={handleSubjectClick} />
          </div>
        );
      case 'quiz':
        return <QuizScreen onBack={navigateBack} onXPGain={handleXPGain} onStreakIncrease={handleStreakIncrease} />;
      case 'game-map-quiz':
        return <GameMapQuizScreen onBack={navigateBack} onXPGain={handleXPGain} onStreakIncrease={handleStreakIncrease} userXP={userXP} streakCount={streakCount} selectedSubject={selectedSubject} onQuizCompletion={handleQuizCompletion} />;
      case 'quiz-completion':
        return <QuizCompletionScreen 
          onBack={navigateBack}
          onRetakeQuiz={handleRetakeQuiz}
          onNextChallenge={handleNextChallenge}
          userXP={userXP}
          xpGained={completionData.xpGained}
          streakCount={streakCount}
          completionTime={completionData.completionTime}
          accuracy={completionData.accuracy}
          totalQuestions={completionData.totalQuestions}
          correctAnswers={completionData.correctAnswers}
          stageName={completionData.stageName}
        />;
      case 'ai':
        return <AITutorScreen onBack={navigateBack} />;
      case 'leaderboard':
        return <LeaderboardScreen onBack={navigateBack} userXP={userXP} />;
      case 'profile':
        return <ProfileScreen onBack={navigateBack} userXP={userXP} streakCount={streakCount} profileImage={profileImage} levelProgress={levelProgress} />;
      case 'videos':
        return <VideosScreen onBack={navigateBack} />;
      case 'subject-detail':
        return selectedSubject ? (
          <SubjectDetailScreen 
            subject={selectedSubject} 
            onBack={navigateBack}
            onStartQuiz={() => navigateToScreen('game-map-quiz')}
            onLessonClick={handleLessonClick}
          />
        ) : null;
      case 'lesson-player':
        return <LessonPlayerScreen 
          onBack={navigateBack} 
          onTakeQuiz={() => navigateToScreen('game-map-quiz')} 
          lessonTitle={selectedLesson || 'Introduction to Algebra'}
        />;
      default:
        return null;
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-orange-50 via-pink-50 to-purple-50 flex items-center justify-center p-2 md:p-4">
      {/* iPhone 14 Mockup Frame - Scaled to 60% */}
      <motion.div
        initial={{ scale: 0.85, opacity: 0, y: 30 }}
        animate={{ scale: 1, opacity: 1, y: 0 }}
        transition={{ duration: 1, ease: "easeOut" }}
        className="relative scale-[0.7] origin-center"
      >
        {/* Device Shadow Layers */}
        <div className="absolute inset-0 bg-black/20 rounded-[3.5rem] blur-3xl transform translate-y-12 scale-110" />
        <div className="absolute inset-0 bg-black/15 rounded-[3.5rem] blur-2xl transform translate-y-8 scale-105" />
        <div className="absolute inset-0 bg-black/10 rounded-[3.5rem] blur-xl transform translate-y-4 scale-102" />
        
        {/* iPhone 14 Frame - Outer Shell */}
        <div className="relative w-[428px] h-[926px] bg-gradient-to-br from-pink-100 via-pink-50 to-pink-200 rounded-[3.5rem] shadow-2xl">
          {/* Frame Reflection/Highlight */}
          <div className="absolute inset-0 bg-gradient-to-br from-white/15 via-transparent to-transparent rounded-[3.5rem] pointer-events-none" />
          <div className="absolute inset-0 bg-gradient-to-tl from-white/5 via-transparent to-transparent rounded-[3.5rem] pointer-events-none" />
          
          {/* Side Buttons */}
          {/* Volume Buttons */}
          <div className="absolute -left-0.5 top-[180px] w-2 h-12 bg-pink-300 rounded-r-md shadow-inner" />
          <div className="absolute -left-0.5 top-[210px] w-2 h-12 bg-pink-300 rounded-r-md shadow-inner" />
          
          {/* Power Button */}
          <div className="absolute -right-0.5 top-[200px] w-2 h-16 bg-pink-300 rounded-l-md shadow-inner" />
          
          {/* Inner Bezel */}
          <div className="absolute inset-2 bg-black rounded-[3.2rem] shadow-inner">
            
            {/* Status Bar positioned at top of frame around notch */}
            <div className="absolute top-0 left-0 right-0 z-60 pt-2">
              <StatusBar textColor={currentScreen === 'videos' ? 'white' : 'black'} />
            </div>
            
            {/* iPhone 16 Dynamic Island */}
            <div className="absolute top-2 left-1/2 transform -translate-x-1/2 w-[126px] h-[37px] bg-black rounded-full shadow-lg z-50">
              {/* Speaker Grille */}
              <div className="absolute top-[8px] left-1/2 transform -translate-x-1/2 w-[50px] h-[3px] bg-gray-900 rounded-full" />
              {/* Front Camera */}
              <div className="absolute top-[6px] left-1/2 transform -translate-x-1/2 translate-x-[18px] w-[6px] h-[6px] bg-gray-800 rounded-full ring-1 ring-gray-700" />
            </div>
            
            {/* Screen Area with proper inner bezel */}
            <div className="absolute inset-1 bg-gradient-to-b from-[#ADC8FF] via-[#E8F2FF]/95 to-white rounded-[3rem] overflow-hidden flex flex-col shadow-inner border border-gray-200/20">
              {/* Content area with top padding for status bar and notch */}
              <div className="pt-12"></div>
              
              {/* Progress Manager - Invisible component for handling saves */}
              <ProgressManager
                userXP={userXP}
                streakCount={streakCount}
                currentProgress={currentProgress}
                totalQuizzesCompleted={totalQuizzesCompleted}
                onProgressLoaded={handleProgressLoaded}
              />

              {/* Main Content - Perfectly scrollable */}
              <div className="flex-1 overflow-y-auto scrollbar-hide relative">
                {/* Opening Animation - No transition wrapper needed */}
                {currentScreen === 'opening' ? (
                  renderScreen()
                ) : (
                  /* Modern Screen Transition Animation for all other screens */
                  <motion.div
                    key={currentScreen}
                    initial={{ 
                      opacity: 0, 
                      scale: currentScreen === 'welcome' ? 0.95 : (currentScreen === 'home' ? 1 : 0.98),
                      y: currentScreen === 'welcome' ? 20 : (currentScreen === 'home' ? 0 : 15),
                      filter: 'blur(8px)'
                    }}
                    animate={{ 
                      opacity: 1, 
                      scale: 1,
                      y: 0,
                      filter: 'blur(0px)'
                    }}
                    exit={{ 
                      opacity: 0, 
                      scale: 0.95,
                      y: -15,
                      filter: 'blur(4px)'
                    }}
                    transition={{ 
                      duration: currentScreen === 'welcome' ? 0.8 : 0.5,
                      ease: currentScreen === 'welcome' ? [0.23, 1, 0.32, 1] : "easeInOut",
                      type: currentScreen === 'welcome' ? "spring" : "tween",
                      bounce: currentScreen === 'welcome' ? 0.25 : 0
                    }}
                  >
                    {/* Enhanced Transition Effects for Welcome Screen */}
                    {currentScreen === 'welcome' && (
                      <>
                        {/* Subtle Particle Background */}
                        <motion.div
                          initial={{ opacity: 0 }}
                          animate={{ opacity: 1 }}
                          exit={{ opacity: 0 }}
                          transition={{ duration: 1.2, ease: "easeOut" }}
                          className="absolute inset-0 pointer-events-none"
                        >
                          {[...Array(12)].map((_, i) => (
                            <motion.div
                              key={i}
                              initial={{ 
                                x: Math.random() * 400,
                                y: Math.random() * 800,
                                opacity: 0,
                                scale: 0
                              }}
                              animate={{ 
                                opacity: [0, 0.4, 0],
                                scale: [0, 1, 0],
                                x: [
                                  Math.random() * 400,
                                  Math.random() * 400,
                                  Math.random() * 400
                                ],
                                y: [
                                  Math.random() * 800,
                                  Math.random() * 800 + 50,
                                  Math.random() * 800 + 100
                                ]
                              }}
                              transition={{
                                duration: 6,
                                delay: Math.random() * 2,
                                repeat: Infinity,
                                ease: "easeInOut"
                              }}
                              className="absolute w-2 h-2 rounded-full"
                              style={{
                                background: `linear-gradient(45deg, #ADC8FF, #091A7A)`,
                                filter: 'blur(1px)'
                              }}
                            />
                          ))}
                        </motion.div>

                        {/* Gradient Overlay for Enhanced Depth */}
                        <motion.div
                          initial={{ opacity: 0 }}
                          animate={{ 
                            opacity: [0, 0.3, 0],
                            background: [
                              'radial-gradient(circle at 30% 20%, #ADC8FF 0%, transparent 50%)',
                              'radial-gradient(circle at 70% 60%, #091A7A 0%, transparent 40%)',
                              'radial-gradient(circle at 20% 80%, #ADC8FF 0%, transparent 60%)'
                            ]
                          }}
                          transition={{ 
                            opacity: { duration: 2, ease: "easeInOut" },
                            background: { duration: 8, repeat: Infinity, ease: "easeInOut" }
                          }}
                          className="absolute inset-0 pointer-events-none"
                        />
                      </>
                    )}

                    {renderScreen()}
                  </motion.div>
                )}
                
                {/* Progress Notification - Inside the phone frame */}
                <ProgressNotification
                  show={showProgressNotification}
                  type={notificationData.type}
                  title={notificationData.title}
                  subtitle={notificationData.subtitle}
                  xpGain={notificationData.xpGain}
                  onComplete={handleNotificationComplete}
                />
                
                {/* Inline XP Notification - Quick feedback */}
                <InlineXPNotification
                  show={showInlineXP}
                  xpGain={recentXPGain}
                />
                
                {/* Progress Save Indicator */}
                <ProgressSaveIndicator
                  show={showIndicator}
                  status={saveStatus}
                />
                
                {/* Bottom padding for navigation and home indicator */}
                <div className={currentScreen === 'subject-detail' || currentScreen === 'lesson-player' || currentScreen === 'game-map-quiz' ? 'h-8' : 'h-28'} />
              </div>
              
              {/* Bottom Navigation - Fixed positioning - Hidden on opening, signup, welcome, subject detail, lesson player, game map quiz, and completion screens */}
              {currentScreen !== 'opening' && currentScreen !== 'signup' && currentScreen !== 'welcome' && currentScreen !== 'subject-detail' && currentScreen !== 'lesson-player' && currentScreen !== 'game-map-quiz' && currentScreen !== 'quiz-completion' && (
                <BottomNavigation currentScreen={currentScreen} onScreenChange={(screen) => {
                  if (screen === 'home') {
                    handleBackToHome();
                  } else {
                    navigateToScreen(screen);
                  }
                }} />
              )}
              
              {/* iPhone Home Indicator */}
              <motion.div 
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 1.2, duration: 0.5 }}
                className="absolute bottom-2 left-1/2 transform -translate-x-1/2 z-50"
              >
                <div className="w-36 h-1 bg-black/60 rounded-full shadow-sm" />
              </motion.div>
            </div>
          </div>
          
          {/* Outer Frame Edge Highlights */}
          <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/5 to-transparent rounded-[3.5rem] pointer-events-none" />
        </div>
        
        {/* Ambient Screen Glow */}
        <div className="absolute inset-3 bg-gradient-to-br from-[#ADC8FF]/10 via-transparent to-transparent rounded-[3rem] pointer-events-none blur-sm" />
        
        {/* Frame Edge Details */}
        <div className="absolute inset-0 rounded-[3.5rem] ring-1 ring-white/10 pointer-events-none" />
      </motion.div>
    </div>
  );
}