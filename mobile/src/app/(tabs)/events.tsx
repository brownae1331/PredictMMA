import React, { useEffect, useState } from 'react';
import { View, Text, StyleSheet, ScrollView, ActivityIndicator } from 'react-native';
import { Image } from 'expo-image';
import { Event } from '../../types/event_types';
import { getUpcomingEvents } from '../../lib/api/event_api';

export default function EventsScreen() {
    const [events, setEvents] = useState<Event[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        fetchUpcomingEvents();
    }, []);

    const fetchUpcomingEvents = async () => {
        try {
            setLoading(true);
            setError(null);
            const events = await getUpcomingEvents();
            setEvents(events);
        } catch (err) {
            setError(err instanceof Error ? err.message : 'An error occurred');
        } finally {
            setLoading(false);
        }
    };

    const renderEventCard = (event: Event, index: number) => {
        return (
            <View key={event.id ?? index}>
                <View style={styles.eventCard}>
                    <View style={styles.eventHeader}>
                        <Text style={styles.eventTitle}>{event.title}</Text>
                        {event.location_flag && (
                            <Image
                                source={{ uri: event.location_flag }}
                                style={styles.flagImage}
                                contentFit="contain"
                                onError={(error) => console.log('Flag image error:', error)}
                            />
                        )}
                    </View>

                    <View style={styles.eventDetails}>
                        <View style={styles.detailRow}>
                            <Text style={styles.detailLabel}>Date & Time:</Text>
                            <Text style={styles.detailValue}>
                                {new Date(event.date).toLocaleDateString()} at {new Date(event.date).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                            </Text>
                        </View>

                        <View style={styles.detailRow}>
                            <Text style={styles.detailLabel}>Organizer:</Text>
                            <Text style={styles.detailValue}>{event.organizer}</Text>
                        </View>

                        <View style={styles.detailRow}>
                            <Text style={styles.detailLabel}>Location:</Text>
                            <Text style={styles.detailValue}>{event.location}</Text>
                        </View>
                    </View>
                </View>

                {/* Separator line between events */}
                {index < events.length - 1 && <View style={styles.separator} />}
            </View>
        );
    };

    return (
        <View style={styles.container}>
            {/* Header Banner */}
            <View style={styles.header}>
                <View style={styles.headerContent}>
                    <Text style={styles.headerText}>Events</Text>
                </View>
            </View>

            {/* Scrollable Content */}
            <ScrollView style={styles.scrollView}>
                <View style={styles.mainContent}>
                    <Text style={styles.welcomeTitle}>Upcoming UFC Events</Text>

                    {loading ? (
                        <ActivityIndicator size="large" color="#000" style={styles.loader} />
                    ) : error ? (
                        <Text style={styles.errorText}>Error: {error}</Text>
                    ) : events.length === 0 ? (
                        <Text style={styles.noEventsText}>No upcoming events found</Text>
                    ) : (
                        events.map((event, eventIndex) => renderEventCard(event, eventIndex))
                    )}
                </View>
            </ScrollView>
        </View>
    );
}

const styles = StyleSheet.create({
    container: {
        flex: 1,
        backgroundColor: '#f5f5f5',
    },
    header: {
        backgroundColor: 'white',
        padding: 10,
        shadowColor: '#000',
        shadowOffset: {
            width: 0,
            height: 2,
        },
        shadowOpacity: 0.1,
        shadowRadius: 3.84,
        elevation: 5,
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
        fontSize: 18,
    },
    scrollView: {
        flex: 1,
    },
    mainContent: {
        paddingHorizontal: 16,
        paddingTop: 20,
        paddingBottom: 20,
    },
    welcomeTitle: {
        fontSize: 24,
        fontWeight: 'bold',
        marginBottom: 20,
        textAlign: 'center',
    },
    loader: {
        marginTop: 50,
    },
    errorText: {
        fontSize: 16,
        color: 'red',
        textAlign: 'center',
        marginTop: 20,
    },
    noEventsText: {
        fontSize: 16,
        color: '#666',
        textAlign: 'center',
        marginTop: 20,
    },
    eventCard: {
        backgroundColor: 'white',
        borderRadius: 12,
        padding: 16,
        marginVertical: 8,
        shadowColor: '#000',
        shadowOffset: {
            width: 0,
            height: 2,
        },
        shadowOpacity: 0.1,
        shadowRadius: 3.84,
        elevation: 3,
    },
    eventHeader: {
        flexDirection: 'row',
        justifyContent: 'space-between',
        alignItems: 'center',
        marginBottom: 12,
    },
    eventTitle: {
        fontSize: 18,
        fontWeight: 'bold',
        color: '#333',
        flex: 1,
        marginRight: 10,
    },
    flagImage: {
        width: 30,
        height: 22,
        marginLeft: 8,
    },
    eventDetails: {
        gap: 8,
    },
    detailRow: {
        flexDirection: 'row',
        alignItems: 'flex-start',
    },
    detailLabel: {
        fontSize: 14,
        fontWeight: '600',
        color: '#666',
        width: 90,
        marginRight: 8,
    },
    detailValue: {
        fontSize: 14,
        color: '#333',
        flex: 1,
    },
    separator: {
        height: 1,
        backgroundColor: '#e0e0e0',
        marginVertical: 12,
        marginHorizontal: 0,
    },
}); 