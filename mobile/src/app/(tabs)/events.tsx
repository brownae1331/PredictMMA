import React, { useEffect, useState } from 'react';
import { View, Text, StyleSheet, FlatList, ActivityIndicator, TouchableOpacity, ListRenderItem } from 'react-native';
import { Image } from 'expo-image';
import { Event } from '../../types/event_types';
import { getUpcomingEvents, getPastEvents } from '../../lib/api/event_api';
import { router } from 'expo-router';

export default function EventsScreen() {
    const [events, setEvents] = useState<Event[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [filter, setFilter] = useState<'upcoming' | 'past'>('upcoming');
    const [page, setPage] = useState(0);
    const PAGE_SIZE = 10;

    useEffect(() => {
        setEvents([]);
        setPage(0);
        fetchEvents(true, 0);
    }, [filter]);

    const fetchEvents = async (reset: boolean = false, requestedOffset: number = 0) => {
        try {
            setLoading(true);
            setError(null);

            let eventsData: Event[] = [];
            if (filter === 'upcoming') {
                eventsData = await getUpcomingEvents(requestedOffset, PAGE_SIZE);
            } else {
                eventsData = await getPastEvents(requestedOffset, PAGE_SIZE);
            }

            if (!reset) {
                setEvents((prev) => [...prev, ...eventsData]);
            } else {
                setEvents(eventsData);
            }
        } catch (err) {
            setError(err instanceof Error ? err.message : 'An error occurred');
        } finally {
            setLoading(false);
        }
    };

    const handleEventPress = (event_id: number) => {
        router.push({
            pathname: '/event-fights',
            params: {
                event_id: event_id
            }
        });
    };

    const renderEventCard: ListRenderItem<Event> = ({ item: event, index }) => {
        return (
            <TouchableOpacity key={event.id} onPress={() => handleEventPress(event.id)}>
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
            </TouchableOpacity>
        );
    };

    const loadMoreEvents = async () => {
        if (loading) return;
        const nextPage = page + 1;
        const newOffset = nextPage * PAGE_SIZE;
        setPage(nextPage);
        await fetchEvents(false, newOffset);
    };

    return (
        <View style={styles.container}>
            {/* Header Banner */}
            <View style={styles.header}>
                <View style={styles.headerContent}>
                    <Text style={styles.headerText}>Events</Text>
                </View>
                <View style={styles.filterContainer}>
                    <TouchableOpacity
                        onPress={() => setFilter('upcoming')}
                        style={[styles.filterButton, filter === 'upcoming' && styles.activeFilterButton]}
                    >
                        <Text style={[styles.filterButtonText, filter === 'upcoming' && styles.activeFilterText]}>Upcoming</Text>
                    </TouchableOpacity>
                    <TouchableOpacity
                        onPress={() => setFilter('past')}
                        style={[styles.filterButton, filter === 'past' && styles.activeFilterButton]}
                    >
                        <Text style={[styles.filterButtonText, filter === 'past' && styles.activeFilterText]}>Past</Text>
                    </TouchableOpacity>
                </View>
            </View>

            {/* Content */}
            <FlatList
                data={events}
                keyExtractor={(item, index) => (item.id ? item.id.toString() : index.toString())}
                renderItem={renderEventCard}
                contentContainerStyle={styles.mainContent}
                ListHeaderComponent={() => (
                    <Text style={styles.welcomeTitle}>
                        {filter === 'upcoming' ? 'Upcoming UFC Events' : 'Past UFC Events'}
                    </Text>
                )}
                ListEmptyComponent={() => (
                    loading ? (
                        <ActivityIndicator size="large" color="#000" style={styles.loader} />
                    ) : error ? (
                        <Text style={styles.errorText}>Error: {error}</Text>
                    ) : (
                        <Text style={styles.noEventsText}>No events found</Text>
                    )
                )}
                ListFooterComponent={() => (
                    loading && events.length > 0 ? <ActivityIndicator size="small" color="#000" style={styles.loader} /> : null
                )}
                onEndReached={loadMoreEvents}
                onEndReachedThreshold={0.5}
            />
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
    // New styles for filter toggle
    filterContainer: {
        flexDirection: 'row',
        justifyContent: 'center',
        marginTop: 10,
    },
    filterButton: {
        paddingVertical: 6,
        paddingHorizontal: 12,
        borderRadius: 20,
        backgroundColor: '#e0e0e0',
        marginHorizontal: 5,
    },
    activeFilterButton: {
        backgroundColor: '#333',
    },
    filterButtonText: {
        color: '#333',
        fontWeight: '600',
    },
    activeFilterText: {
        color: '#fff',
    },
}); 