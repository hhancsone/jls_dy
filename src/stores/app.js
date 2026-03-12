import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useAppStore = defineStore('app', () => {
  const comments = ref([])
  const timeSeriesData = ref([])
  const keywordData = ref([])
  
  const addComments = (newComments) => {
    comments.value = [...comments.value, ...newComments]
  }
  
  const clearComments = () => {
    comments.value = []
  }
  
  const setTimeSeriesData = (data) => {
    timeSeriesData.value = data
  }
  
  const setKeywordData = (data) => {
    keywordData.value = data
  }
  
  const getSentimentStats = () => {
    const total = comments.value.length
    const positive = comments.value.filter(c => c.sentiment?.type === 'positive').length
    const negative = comments.value.filter(c => c.sentiment?.type === 'negative').length
    const neutral = comments.value.filter(c => c.sentiment?.type === 'neutral').length
    
    return {
      total,
      positive,
      negative,
      neutral,
      positiveRatio: total > 0 ? Math.round((positive / total) * 100) : 0,
      negativeRatio: total > 0 ? Math.round((negative / total) * 100) : 0,
      neutralRatio: total > 0 ? Math.round((neutral / total) * 100) : 0
    }
  }
  
  return {
    comments,
    timeSeriesData,
    keywordData,
    addComments,
    clearComments,
    setTimeSeriesData,
    setKeywordData,
    getSentimentStats
  }
})
