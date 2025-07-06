import React, { useCallback, useState } from 'react';
import {
    View,
    Text,
    StyleSheet,
    SectionList,
    RefreshControl,
} from 'react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { jwtDecode } from 'jwt-decode';
import { useFocusEffect } from 'expo-router';

import { getAllPredictions } from '../../lib/api/predict_api';
import { getEventSummaryByUrl } from '../../lib/api/ufc_api';
import { Prediction } from '../../types/predict_types';

interface JwtPayload {
    sub: string; // user id as string
    exp: number;
    iat?: number;
}

interface PredictionSection {
    title: string; // Human-readable event title (with date)
    data: Prediction[];
}

export default function PredictScreen() {
    const [sections, setSections] = useState<PredictionSection[]>([]);
    const [loading, setLoading] = useState<boolean>(false);

    const fetchPredictions = useCallback(async () => {
        setLoading(true);
        try {
            const token = await AsyncStorage.getItem('access_token');
            if (!token) return;

            const decoded = jwtDecode<JwtPayload>(token);
            const userId = parseInt(decoded.sub, 10);

            const predictions = await getAllPredictions(userId, token);

            // Group predictions by event_url
            const grouped: Record<string, Prediction[]> = {};
            predictions.forEach((pred) => {
                if (!grouped[pred.event_url]) {
                    grouped[pred.event_url] = [];
                }
                grouped[pred.event_url].push(pred);
            });

            // Build each section (with eventDateMs helper) and then sort by date ascending
            const sectionsWithDate = await Promise.all(
                Object.keys(grouped).map(async (eventUrl) => {
                    let eventTitle = eventUrl; // Fallback to url if title not found
                    let eventDateMs = Number.MAX_SAFE_INTEGER;

                    try {
                        const summary = await getEventSummaryByUrl(eventUrl);
                        const date = new Date(summary.event_date);
                        eventDateMs = date.getTime();
                        const formattedDate = date.toLocaleDateString(undefined, {
                            year: 'numeric',
                            month: 'short',
                            day: 'numeric',
                        });
                        eventTitle = `${summary.event_title} • ${formattedDate}`;
                    } catch (e) {
                        console.warn(`Could not fetch event title for ${eventUrl}`);
                    }

                    // Sort predictions within the section by fight_idx
                    const sortedData = [...grouped[eventUrl]].sort((a, b) => a.fight_idx - b.fight_idx);

                    return {
                        eventDateMs,
                        section: {
                            title: eventTitle,
                            data: sortedData,
                        } as PredictionSection,
                    };
                })
            );

            // Sort by date ascending (soonest first)
            sectionsWithDate.sort((a, b) => a.eventDateMs - b.eventDateMs);

            setSections(sectionsWithDate.map((item) => item.section));
        } catch (err) {
            console.error('Failed to load predictions', err);
        } finally {
            setLoading(false);
        }
    }, []);

    // Automatically refresh predictions whenever this screen/tab comes into focus
    useFocusEffect(
        useCallback(() => {
            fetchPredictions();
        }, [fetchPredictions])
    );

    return (
        <View style={styles.container}>
            {/* Header Banner */}
            <View style={styles.header}>
                <View style={styles.headerContent}>
                    <Text style={styles.headerText}>My Predictions</Text>
                </View>
            </View>

            {/* Predictions List */}
            <SectionList
                sections={sections}
                keyExtractor={(item) => `${item.event_url}-${item.fight_id}`}
                renderSectionHeader={({ section: { title } }) => (
                    <View style={styles.sectionHeader}>
                        <Text style={styles.sectionHeaderText}>{title}</Text>
                    </View>
                )}
                renderItem={({ item }) => (
                    <View style={styles.predictionItem}>
                        <Text style={styles.predictionFight}>{`Fight #${item.fight_idx}`}</Text>
                        <Text style={styles.predictionText}>{
                            `${item.fighter_prediction} – ${item.method_prediction}` +
                            (item.round_prediction ? ` (Round ${item.round_prediction})` : '')
                        }</Text>
                    </View>
                )}
                ListEmptyComponent={() => (
                    <View style={styles.emptyContainer}>
                        <Text style={styles.emptyText}>No predictions yet.</Text>
                    </View>
                )}
                refreshControl={
                    <RefreshControl refreshing={loading} onRefresh={fetchPredictions} />
                }
                contentContainerStyle={sections.length === 0 ? styles.flexGrow : undefined}
            />
        </View>
    );
}

const styles = StyleSheet.create({
    container: {
        flex: 1,
        backgroundColor: '#f9fafb',
    },
    header: {
        backgroundColor: 'white',
        paddingVertical: 10,
        borderBottomWidth: StyleSheet.hairlineWidth,
        borderColor: '#e5e7eb',
    },
    headerContent: {
        flexDirection: 'row',
        alignItems: 'center',
        justifyContent: 'center',
        marginTop: 50,
    },
    headerText: {
        color: 'black',
        fontWeight: 'bold',
        fontSize: 20,
    },
    sectionHeader: {
        backgroundColor: '#e5e7eb',
        paddingVertical: 6,
        paddingHorizontal: 12,
    },
    sectionHeaderText: {
        fontWeight: 'bold',
        fontSize: 16,
        color: '#111827',
    },
    predictionItem: {
        paddingVertical: 8,
        paddingHorizontal: 16,
        borderBottomWidth: StyleSheet.hairlineWidth,
        borderColor: '#d1d5db',
        backgroundColor: 'white',
    },
    predictionFight: {
        fontSize: 14,
        fontWeight: '600',
        color: '#374151',
    },
    predictionText: {
        fontSize: 14,
        color: '#4b5563',
    },
    emptyContainer: {
        flex: 1,
        justifyContent: 'center',
        alignItems: 'center',
        paddingTop: 40,
    },
    emptyText: {
        fontSize: 16,
        color: '#6b7280',
    },
    flexGrow: {
        flexGrow: 1,
    },
});