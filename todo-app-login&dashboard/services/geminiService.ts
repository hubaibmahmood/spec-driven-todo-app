import { GoogleGenAI, Type } from "@google/genai";
import { Priority } from "../types";

// Initialize Gemini
// Note: In a production app, handle the missing key more gracefully or prompt the user.
const apiKey = process.env.API_KEY || '';
const ai = apiKey ? new GoogleGenAI({ apiKey }) : null;

export const enhanceTaskContent = async (draftTitle: string): Promise<{ title: string; description: string; priority: Priority; tags: string[] }> => {
  if (!ai) throw new Error("API Key is missing");
  
  const model = "gemini-2.5-flash";

  const response = await ai.models.generateContent({
    model,
    contents: `Enhance this draft todo task: "${draftTitle}". Provide a more professional title, a brief actionable description, a suggested priority based on urgency implication, and 2-3 relevant tags.`,
    config: {
      responseMimeType: "application/json",
      responseSchema: {
        type: Type.OBJECT,
        properties: {
          title: { type: Type.STRING },
          description: { type: Type.STRING },
          priority: { type: Type.STRING, enum: [Priority.LOW, Priority.MEDIUM, Priority.HIGH, Priority.URGENT] },
          tags: { type: Type.ARRAY, items: { type: Type.STRING } }
        },
        required: ["title", "description", "priority", "tags"]
      }
    }
  });

  const text = response.text;
  if (!text) throw new Error("No response from AI");

  return JSON.parse(text);
};

export const suggestSubtasks = async (taskTitle: string, taskDescription: string): Promise<string[]> => {
  if (!ai) throw new Error("API Key is missing");

  const model = "gemini-2.5-flash";

  const response = await ai.models.generateContent({
    model,
    contents: `Break down the task "${taskTitle}" (${taskDescription}) into 3-5 concise, actionable subtasks.`,
    config: {
      responseMimeType: "application/json",
      responseSchema: {
        type: Type.ARRAY,
        items: { type: Type.STRING }
      }
    }
  });

  const text = response.text;
  if (!text) throw new Error("No response from AI");

  return JSON.parse(text);
};