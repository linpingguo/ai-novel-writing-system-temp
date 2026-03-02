import { useState, useEffect } from 'react'
import { useParams } from 'react-router-dom'
import api from '../lib/api'

interface Chapter {
  id: string
  title: string
  content: string
  word_count: number
}

export default function ConsistencyCheck() {
  const { id: projectId } = useParams<{ id: string }>()
  const [chapters, setChapters] = useState<Chapter[]>([])
  const [loading, setLoading] = useState(true)
  const [checkedChapters, setCheckedChapters] = useState<Set<string>>(new Set())
  const [inconsistencies, setInconsistencies] = useState<string[]>([])

  useEffect(() => {
    fetchChapters()
  }, [projectId])

  const fetchChapters = async () => {
    try {
      const response = await api.get(`/projects/${projectId}/chapters`)
      setChapters(response.data || [])
    } catch (err) {
      console.error('Failed to fetch chapters:', err)
    } finally {
      setLoading(false)
    }
  }

  const checkCharacterConsistency = (content: string, characterName: string) => {
    const characterMentions = content.match(new RegExp(`${characterName}`, 'gi'))
    if (!characterMentions || characterMentions.length === 0) {
      return {
        type: 'missing_character',
        description: `角色 ${characterName} 未在章节中提及`
      }
    }
    return null
  }

  const handleCheckChapter = (chapterId: string, characterName: string) => {
    const chapter = chapters.find(c => c.id === chapterId)
    if (!chapter) return

    const inconsistency = checkCharacterConsistency(chapter.content, characterName)
    if (inconsistency) {
      setInconsistencies(prev => [...prev, inconsistency])
    }

    if (inconsistency) {
      setCheckedChapters(prev => new Set([...prev, chapterId]))
    } else {
      setCheckedChapters(prev => {
        const newSet = new Set(prev)
        newSet.delete(chapterId)
        return newSet
      })
    }
  }

  const getConsistencyScore = () => {
    const totalChecks = chapters.length
    const completedChecks = checkedChapters.size
    const issuesFound = inconsistencies.length

    const score = totalChecks > 0
      ? Math.round(((completedChecks - issuesFound) / totalChecks) * 100)
      : 100

    return score
  }

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-gray-600">加载中...</div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="container mx-auto px-4 py-8">
        <div className="mb-6">
          <a href={`/projects/${projectId}`} className="text-gray-600 hover:text-gray-900">
            ← 返回项目
          </a>
          <h1 className="text-3xl font-bold">角色设定一致性检测</h1>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2 bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-bold mb-4">检测结果</h2>

            <div className="mb-4 p-4 bg-gray-50 rounded">
              <div className="text-4xl font-bold mb-2">
                一致性评分
              </div>
              <div className="text-6xl font-bold text-green-600">
                {getConsistencyScore()}%
              </div>
            </div>

            <div className="space-y-3">
              <div className="flex justify-between items-center p-3 bg-blue-50 rounded">
                <span className="font-medium">检查的章节数</span>
                <span className="text-2xl font-bold">{chapters.length}</span>
              </div>
              <div className="flex justify-between items-center p-3 bg-green-50 rounded">
                <span className="font-medium">已完成检查</span>
                <span className="text-2xl font-bold">{checkedChapters.size}</span>
              </div>
              <div className="flex justify-between items-center p-3 bg-red-50 rounded">
                <span className="font-medium">发现问题</span>
                <span className="text-2xl font-bold text-red-600">{inconsistencies.length}</span>
              </div>
            </div>

            {inconsistencies.length > 0 && (
              <div className="mt-6">
                <h3 className="text-lg font-bold mb-4">发现的问题</h3>
                <div className="space-y-2">
                  {inconsistencies.map((issue, index) => (
                    <div key={index} className="p-3 bg-red-50 rounded border border-red-200">
                      <p className="text-sm font-medium text-red-800">
                        {issue.description}
                      </p>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-bold mb-4">章节检查</h2>

            {chapters.length > 0 ? (
              <div className="space-y-2">
                {chapters.map((chapter) => (
                  <div
                    key={chapter.id}
                    className="p-4 border border-gray-200 rounded hover:border-blue-300 transition-colors"
                  >
                    <div className="flex justify-between items-start mb-2">
                      <div>
                        <h3 className="font-bold">{chapter.title}</h3>
                        <p className="text-sm text-gray-600">
                          字数: {chapter.word_count}
                        </p>
                      </div>
                      <button
                        onClick={() => handleCheckChapter(chapter.id, '主角')}
                        className="bg-green-600 hover:bg-green-700 text-white px-3 py-1 rounded text-sm"
                      >
                        检查主角
                      </button>
                      <button
                        onClick={() => handleCheckChapter(chapter.id, '女主角')}
                        className="bg-blue-600 hover:bg-blue-700 text-white px-3 py-1 rounded text-sm"
                      >
                        检查女主角
                      </button>
                    </div>
                  </div>

                  <div className="mt-3 p-3 bg-blue-50 rounded">
                    {checkedChapters.has(chapter.id) ? (
                      <div className="flex items-center gap-2">
                        <span className="text-green-600">✓</span>
                        <span className="text-sm">已检查</span>
                      </div>
                    ) : (
                      <span className="text-gray-400">○</span>
                      )}
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-12 text-gray-600">
                还没有章节,请先创建章节
              </div>
            )}
          </div>
        </div>
      </div>
    )
  }
}
